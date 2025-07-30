import time
from collections import OrderedDict, defaultdict
from typing import Any, Callable, Optional, Union, Dict, List, Tuple
from functools import wraps, update_wrapper
import pickle
import hashlib
import threading
import json
import inspect
import zlib
from datetime import timedelta
import logging

# 设置日志
logger = logging.getLogger(__name__)

class CachePolicy:
    """缓存策略基类"""
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
    
    def on_get(self, key: Any) -> None:
        """当获取缓存项时调用"""
        pass
    
    def on_set(self, key: Any) -> None:
        """当设置缓存项时调用"""
        pass
    
    def on_delete(self, key: Any) -> None:
        """当删除缓存项时调用"""
        pass
    
    def on_miss(self, key: Any) -> None:
        """当缓存未命中时调用"""
        pass
    
    def on_evict(self, key: Any) -> None:
        """当淘汰缓存项时调用"""
        pass
    
    def evict(self) -> Any:
        """根据策略淘汰一个缓存项，返回被淘汰的键"""
        raise NotImplementedError
    
    def clear(self) -> None:
        """清除策略状态"""
        pass

class LRUPolicy(CachePolicy):
    """最近最少使用策略"""
    def __init__(self, maxsize: int = 128):
        super().__init__(maxsize)
        self._order = OrderedDict()
    
    def on_get(self, key: Any) -> None:
        if key in self._order:
            self._order.move_to_end(key)
    
    def on_set(self, key: Any) -> None:
        self._order[key] = True
        self._order.move_to_end(key)
        if len(self._order) > self.maxsize:
            self.evict()
    
    def on_delete(self, key: Any) -> None:
        self._order.pop(key, None)
    
    def on_evict(self, key: Any) -> None:
        self._order.pop(key, None)
    
    def evict(self) -> Any:
        if not self._order:
            raise ValueError("Cache is empty")
        key, _ = self._order.popitem(last=False)
        return key
    
    def clear(self) -> None:
        self._order.clear()

class LFUPolicy(CachePolicy):
    """最不经常使用策略"""
    def __init__(self, maxsize: int = 128):
        super().__init__(maxsize)
        self._counts = defaultdict(int)
        self._min_heap = []
    
    def on_get(self, key: Any) -> None:
        self._counts[key] += 1
    
    def on_set(self, key: Any) -> None:
        self._counts[key] = 1
        if len(self._counts) > self.maxsize:
            self.evict()
    
    def on_delete(self, key: Any) -> None:
        self._counts.pop(key, None)
    
    def on_evict(self, key: Any) -> None:
        self._counts.pop(key, None)
    
    def evict(self) -> Any:
        if not self._counts:
            raise ValueError("Cache is empty")
        
        # 找到使用次数最少的键
        min_key = min(self._counts.keys(), key=lambda k: self._counts[k])
        del self._counts[min_key]
        return min_key
    
    def clear(self) -> None:
        self._counts.clear()

class FIFOPolicy(CachePolicy):
    """先进先出策略"""
    def __init__(self, maxsize: int = 128):
        super().__init__(maxsize)
        self._queue = []
    
    def on_set(self, key: Any) -> None:
        self._queue.append(key)
        if len(self._queue) > self.maxsize:
            self.evict()
    
    def on_delete(self, key: Any) -> None:
        if key in self._queue:
            self._queue.remove(key)
    
    def on_evict(self, key: Any) -> None:
        if key in self._queue:
            self._queue.remove(key)
    
    def evict(self) -> Any:
        if not self._queue:
            raise ValueError("Cache is empty")
        return self._queue.pop(0)
    
    def clear(self) -> None:
        self._queue.clear()

class CacheItem:
    """缓存项"""
    __slots__ = ['value', 'expire_time', 'hits', 'last_accessed', 'size']
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.expire_time = time.time() + ttl if ttl else None
        self.hits = 0
        self.last_accessed = time.time()
        self.size = self._calculate_size(value)
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        return self.expire_time is not None and time.time() > self.expire_time
    
    def hit(self) -> None:
        """增加命中计数"""
        self.hits += 1
        self.last_accessed = time.time()
    
    def _calculate_size(self, value: Any) -> int:
        """估算缓存项大小"""
        try:
            return len(pickle.dumps(value))
        except:
            return 1  # 无法计算大小时返回1

class SmartCache:
    """智能缓存"""
    def __init__(
        self,
        policy: Union[str, CachePolicy] = 'lru',
        maxsize: int = 128,
        maxmem: Optional[int] = None,
        ttl: Optional[float] = None,
        serializer: Optional[Callable[[Any], bytes]] = None,
        deserializer: Optional[Callable[[bytes], Any]] = None,
        namespace: str = 'default',
        compression: bool = False
    ):
        """
        初始化智能缓存
        
        参数:
            policy: 缓存策略 ('lru', 'lfu', 'fifo' 或 CachePolicy 实例)
            maxsize: 最大缓存项数
            maxmem: 最大内存使用量(MB)，None表示不限制
            ttl: 默认生存时间(秒)，None表示永不过期
            serializer: 自定义序列化函数
            deserializer: 自定义反序列化函数
            namespace: 缓存命名空间
            compression: 是否启用压缩
        """
        self._data: Dict[Any, CacheItem] = {}
        self._lock = threading.RLock()
        self.maxsize = maxsize
        self.maxmem = maxmem * 1024 * 1024 if maxmem else None  # 转换为字节
        self.default_ttl = ttl
        self.namespace = namespace
        self.compression = compression
        self.total_size = 0  # 当前总大小(字节)
        
        self.stats = {
            'hits': 0, 
            'misses': 0, 
            'evictions': 0, 
            'expired': 0,
            'size': 0,
            'compression_ratio': 0.0
        }
        
        # 设置序列化器
        self.serializer = serializer or pickle.dumps
        self.deserializer = deserializer or pickle.loads
        
        # 设置缓存策略
        if isinstance(policy, str):
            policy = policy.lower()
            if policy == 'lru':
                self.policy = LRUPolicy(maxsize)
            elif policy == 'lfu':
                self.policy = LFUPolicy(maxsize)
            elif policy == 'fifo':
                self.policy = FIFOPolicy(maxsize)
            else:
                raise ValueError(f"Unknown cache policy: {policy}")
        elif isinstance(policy, CachePolicy):
            self.policy = policy
        else:
            raise TypeError("policy must be str or CachePolicy instance")
    
    def __len__(self) -> int:
        """当前缓存项数量"""
        return len(self._data)
    
    def __contains__(self, key: Any) -> bool:
        """检查键是否在缓存中(未过期)"""
        try:
            self._get(key, update_stats=False)
            return True
        except KeyError:
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._data.clear()
            self.policy.clear()
            self.total_size = 0
            self.stats = {
                'hits': 0, 
                'misses': 0, 
                'evictions': 0, 
                'expired': 0,
                'size': 0,
                'compression_ratio': 0.0
            }
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        获取缓存值
        
        参数:
            key: 缓存键
            default: 未找到时返回的默认值
            
        返回:
            缓存值或默认值
        """
        try:
            return self._get(key)
        except KeyError:
            return default
    
    def _get(self, key: Any, update_stats: bool = True) -> Any:
        """内部获取方法，不处理默认值"""
        with self._lock:
            if key not in self._data:
                if update_stats:
                    self.stats['misses'] += 1
                    self.policy.on_miss(key)
                raise KeyError(key)
            
            item = self._data[key]
            if item.is_expired():
                del self._data[key]
                self.total_size -= item.size
                if update_stats:
                    self.stats['expired'] += 1
                    self.policy.on_miss(key)
                raise KeyError(f"Key {key} expired")
            
            item.hit()
            if update_stats:
                self.stats['hits'] += 1
                self.policy.on_get(key)
            return item.value
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """
        设置缓存值
        
        参数:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间(秒)，None表示使用默认ttl
        """
        with self._lock:
            # 如果键已存在，先删除
            if key in self._data:
                self._delete(key, update_stats=False)
            
            # 检查是否需要淘汰
            while len(self._data) >= self.maxsize or (
                self.maxmem is not None and self.total_size >= self.maxmem
            ):
                self._evict()
            
            # 压缩数据
            if self.compression:
                try:
                    value = self._compress(value)
                except Exception as e:
                    logger.warning(f"Compression failed: {str(e)}")
            
            ttl = ttl if ttl is not None else self.default_ttl
            item = CacheItem(value, ttl)
            self._data[key] = item
            self.total_size += item.size
            self.policy.on_set(key)
            self.stats['size'] = self.total_size
    
    def _compress(self, data: Any) -> Any:
        """压缩数据"""
        serialized = self.serializer(data)
        compressed = zlib.compress(serialized)
        self.stats['compression_ratio'] = len(compressed) / len(serialized)
        return compressed
    
    def _decompress(self, data: Any) -> Any:
        """解压数据"""
        if not self.compression:
            return data
        return self.deserializer(zlib.decompress(data))
    
    def delete(self, key: Any) -> bool:
        """
        删除缓存项
        
        返回:
            是否成功删除
        """
        with self._lock:
            return self._delete(key)
    
    def _delete(self, key: Any, update_stats: bool = True) -> bool:
        """内部删除方法"""
        if key in self._data:
            item = self._data[key]
            del self._data[key]
            self.total_size -= item.size
            if update_stats:
                self.policy.on_delete(key)
            return True
        return False
    
    def _evict(self) -> None:
        """根据策略淘汰一个缓存项"""
        with self._lock:
            try:
                key = self.policy.evict()
                if key in self._data:
                    item = self._data[key]
                    del self._data[key]
                    self.total_size -= item.size
                    self.stats['evictions'] += 1
                    self.policy.on_evict(key)
            except ValueError:
                pass  # 缓存为空
    
    def keys(self) -> List[Any]:
        """获取所有未过期的键"""
        with self._lock:
            return [k for k in self._data if not self._data[k].is_expired()]
    
    def values(self) -> List[Any]:
        """获取所有未过期的值"""
        with self._lock:
            return [self._get(k) for k in self.keys()]
    
    def items(self) -> List[Tuple[Any, Any]]:
        """获取所有未过期的键值对"""
        with self._lock:
            return [(k, self._get(k)) for k in self.keys()]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            stats = self.stats.copy()
            stats.update({
                'current_size': len(self._data),
                'max_size': self.maxsize,
                'memory_usage': f"{self.total_size / (1024 * 1024):.2f}MB",
                'max_memory': f"{self.maxmem / (1024 * 1024):.2f}MB" if self.maxmem else "unlimited",
                'namespace': self.namespace,
                'policy': self.policy.__class__.__name__,
                'compression': self.compression,
                'avg_hit_rate': stats['hits'] / max(1, stats['hits'] + stats['misses'])
            })
            return stats
    
    def persist(self, filepath: str) -> None:
        """持久化缓存到文件"""
        with self._lock:
            data = {
                'items': {k: (self.serializer(v.value), v.expire_time) 
                         for k, v in self._data.items() 
                         if not v.is_expired()},
                'stats': self.stats,
                'namespace': self.namespace,
                'compression': self.compression
            }
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
    
    def load(self, filepath: str) -> None:
        """从文件加载缓存"""
        with self._lock:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            if data.get('namespace') != self.namespace:
                raise ValueError("Namespace mismatch")
            
            self.clear()
            self.compression = data.get('compression', False)
            
            for k, v in data['items'].items():
                value = self.deserializer(v[0])
                if self.compression:
                    value = self._decompress(value)
                
                ttl = (v[1] - time.time()) if v[1] is not None else None
                self._data[k] = CacheItem(value, ttl)
            
            self.stats = data['stats']
    
    def memoize(
        self, 
        ttl: Optional[float] = None, 
        key_func: Optional[Callable] = None,
        unless: Optional[Callable] = None
    ):
        """
        装饰器，缓存函数结果
        
        参数:
            ttl: 生存时间(秒)
            key_func: 自定义缓存键生成函数
            unless: 条件函数，返回True时不缓存
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 检查是否应该跳过缓存
                if unless and unless(*args, **kwargs):
                    return func(*args, **kwargs)
                
                cache_key = self._make_cache_key(func, args, kwargs, key_func)
                try:
                    return self.get(cache_key)
                except KeyError:
                    result = func(*args, **kwargs)
                    self.set(cache_key, result, ttl)
                    return result
            
            def invalidate(*args, **kwargs):
                """使缓存项失效"""
                cache_key = self._make_cache_key(func, args, kwargs, key_func)
                self.delete(cache_key)
            
            wrapper.invalidate = invalidate
            return wrapper
        return decorator
    
    def _make_cache_key(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        key_func: Optional[Callable] = None
    ) -> str:
        """生成缓存键"""
        if key_func:
            return key_func(func, args, kwargs)
        
        # 获取函数签名
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # 生成键
        key_parts = [
            func.__module__,
            func.__qualname__,
            str(bound_args.arguments)
        ]
        key = "|".join(key_parts)
        return hashlib.sha256(key.encode('utf-8')).hexdigest()
    
    def ttl(self, key: Any) -> Optional[float]:
        """
        获取剩余生存时间(秒)
        
        返回:
            剩余时间(秒)，None表示永不过期，-1表示键不存在或已过期
        """
        with self._lock:
            if key not in self._data:
                return -1
            
            item = self._data[key]
            if item.is_expired():
                return -1
            
            if item.expire_time is None:
                return None
            
            return max(0, item.expire_time - time.time())
    
    def expire(self, key: Any, ttl: float) -> bool:
        """
        设置键的生存时间
        
        参数:
            key: 缓存键
            ttl: 生存时间(秒)
            
        返回:
            是否设置成功
        """
        with self._lock:
            if key not in self._data or self._data[key].is_expired():
                return False
            
            self._data[key].expire_time = time.time() + ttl
            return True
    
    def touch(self, key: Any) -> bool:
        """
        更新键的最后访问时间
        
        返回:
            是否更新成功
        """
        with self._lock:
            if key not in self._data or self._data[key].is_expired():
                return False
            
            self._data[key].last_accessed = time.time()
            self.policy.on_get(key)
            return True

def create_cache(namespace: str = 'default', **kwargs) -> SmartCache:
    """创建缓存实例的工厂函数"""
    return SmartCache(namespace=namespace, **kwargs)

# 全局默认缓存
default_cache = SmartCache()