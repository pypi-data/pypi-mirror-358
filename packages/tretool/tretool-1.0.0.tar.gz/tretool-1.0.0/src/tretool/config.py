import json
import os
import threading
from typing import Any, Callable, Dict, Optional, Union, List, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import logging
from copy import deepcopy

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class ConfigError(Exception):
    """配置基础异常"""
    pass

class ConfigLockedError(ConfigError):
    """配置被锁定异常"""
    pass

class ConfigValidationError(ConfigError):
    """配置验证失败异常"""
    pass

class ConfigOperation(Enum):
    """配置操作类型"""
    SET = auto()
    DELETE = auto()
    RESET = auto()

@dataclass
class ConfigChangeEvent:
    """配置变更事件"""
    key: str
    old_value: Any
    new_value: Any
    operation: ConfigOperation

class ConfigValidator(Generic[T]):
    """配置验证器基类"""
    def validate(self, value: Any) -> T:
        """验证并转换配置值"""
        raise NotImplementedError

class IntValidator(ConfigValidator[int]):
    """整数验证器"""
    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None):
        self.min = min_value
        self.max = max_value
    
    def validate(self, value: Any) -> int:
        try:
            val = int(value)
            if self.min is not None and val < self.min:
                raise ConfigValidationError(f"值 {val} 小于最小值 {self.min}")
            if self.max is not None and val > self.max:
                raise ConfigValidationError(f"值 {val} 大于最大值 {self.max}")
            return val
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"无效的整数值: {value}") from e

class Config:
    """
    增强版配置管理类，提供类型安全、线程安全的配置管理
    
    主要特性:
    - 类型安全的配置存取
    - 配置变更监听和通知
    - 配置验证和转换
    - 多格式持久化支持
    - 原子操作和事务支持
    - 配置版本控制
    - 环境变量集成
    """
    
    def __init__(
        self,
        initial_config: Optional[Dict[str, Any]] = None,
        validators: Optional[Dict[str, ConfigValidator]] = None,
        config_dir: Optional[Union[str, Path]] = None,
        env_prefix: Optional[str] = None
    ):
        """
        初始化配置存储
        
        参数:
            initial_config: 初始配置字典
            validators: 配置验证器字典 {key: validator}
            config_dir: 配置文件存储目录
            env_prefix: 环境变量前缀
        """
        self._data = deepcopy(initial_config) if initial_config else {}
        self._validators = validators or {}
        self._lock = threading.Lock()
        self._change_listeners = []
        self._config_dir = Path(config_dir) if config_dir else None
        self._env_prefix = f"{env_prefix}_" if env_prefix else ""
        self._version = 1
        self._transaction_stack = []
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def __str__(self) -> str:
        """返回配置的可读字符串表示"""
        return json.dumps(self._data, indent=2, ensure_ascii=False)
    
    def __repr__(self) -> str:
        """返回配置的正式表示"""
        return f"Config({self._data})"
    
    def __contains__(self, key: str) -> bool:
        """检查配置项是否存在"""
        return key in self._data
    
    def __len__(self) -> int:
        """返回配置项的数量"""
        return len(self._data)
    
    def __enter__(self):
        """进入事务上下文"""
        self.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出事务上下文"""
        if exc_type is None:
            self.commit_transaction()
        else:
            self.rollback_transaction()
    
    @property
    def version(self) -> int:
        """获取配置版本"""
        return self._version
    
    def begin_transaction(self):
        """开始一个配置事务"""
        with self._lock:
            self._transaction_stack.append(deepcopy(self._data))
    
    def commit_transaction(self):
        """提交当前事务"""
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("没有活跃的事务可提交")
            self._transaction_stack.pop()
            self._version += 1
    
    def rollback_transaction(self):
        """回滚当前事务"""
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("没有活跃的事务可回滚")
            self._data = self._transaction_stack.pop()
    
    def add_change_listener(self, listener: Callable[[ConfigChangeEvent], None]):
        """
        添加配置变更监听器
        
        参数:
            listener: 回调函数，接收 ConfigChangeEvent 参数
        """
        with self._lock:
            if listener not in self._change_listeners:
                self._change_listeners.append(listener)
    
    def remove_change_listener(self, listener: Callable[[ConfigChangeEvent], None]):
        """移除配置变更监听器"""
        with self._lock:
            if listener in self._change_listeners:
                self._change_listeners.remove(listener)
    
    def _notify_change(self, event: ConfigChangeEvent):
        """通知所有监听器配置变更"""
        with self._lock:
            listeners = self._change_listeners.copy()
        
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"配置变更通知错误: {e}", exc_info=True)
    
    def get(self, key: str, default: Any = None, validate: bool = True) -> Any:
        """
        获取配置项
        
        参数:
            key: 配置键名
            default: 默认值
            validate: 是否验证返回值
            
        返回:
            配置值或默认值
            
        异常:
            ConfigValidationError: 验证失败
        """
        with self._lock:
            value = self._data.get(key, default)
        
        if validate and key in self._validators:
            try:
                return self._validators[key].validate(value)
            except ConfigValidationError as e:
                logger.warning(f"配置验证失败 [{key}]: {e}")
                raise
        
        return value
    
    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """
        设置配置项
        
        参数:
            key: 配置键名
            value: 配置值
            validate: 是否验证值
            
        返回:
            True 设置成功, False 设置失败
            
        异常:
            ConfigValidationError: 验证失败
            ConfigLockedError: 配置被锁定
        """
        if validate and key in self._validators:
            value = self._validators[key].validate(value)
        
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("必须在事务中修改配置")
            
            old_value = self._data.get(key)
            self._data[key] = value
            
            # 通知变更
            event = ConfigChangeEvent(
                key=key,
                old_value=old_value,
                new_value=value,
                operation=ConfigOperation.SET
            )
            self._notify_change(event)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        删除配置项
        
        参数:
            key: 要删除的配置键名
            
        返回:
            True 删除成功, False 键不存在
            
        异常:
            ConfigLockedError: 配置被锁定
        """
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("必须在事务中修改配置")
            
            if key not in self._data:
                return False
                
            old_value = self._data[key]
            del self._data[key]
            
            # 通知变更
            event = ConfigChangeEvent(
                key=key,
                old_value=old_value,
                new_value=None,
                operation=ConfigOperation.DELETE
            )
            self._notify_change(event)
            
            return True
    
    def has(self, key: str) -> bool:
        """检查配置项是否存在"""
        with self._lock:
            return key in self._data
    
    def bulk_update(self, updates: Dict[str, Any], validate: bool = True) -> bool:
        """
        批量更新配置
        
        参数:
            updates: 包含多个键值对的字典
            validate: 是否验证值
            
        返回:
            True 更新成功
            
        异常:
            ConfigValidationError: 验证失败
            ConfigLockedError: 配置被锁定
        """
        if validate:
            for key, value in updates.items():
                if key in self._validators:
                    updates[key] = self._validators[key].validate(value)
        
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("必须在事务中修改配置")
            
            # 记录变更
            changes = []
            for key, value in updates.items():
                old_value = self._data.get(key)
                self._data[key] = value
                changes.append(ConfigChangeEvent(
                    key=key,
                    old_value=old_value,
                    new_value=value,
                    operation=ConfigOperation.SET
                ))
            
            # 批量通知变更
            for event in changes:
                self._notify_change(event)
            
            return True
    
    def reset(self, new_config: Optional[Dict[str, Any]] = None) -> None:
        """
        重置所有配置
        
        参数:
            new_config: 新的配置字典 (可选，默认清空)
            
        异常:
            ConfigLockedError: 配置被锁定
        """
        with self._lock:
            if not self._transaction_stack:
                raise ConfigError("必须在事务中修改配置")
            
            # 记录所有变更（删除）
            delete_events = []
            for key in list(self._data.keys()):
                delete_events.append(ConfigChangeEvent(
                    key=key,
                    old_value=self._data[key],
                    new_value=None,
                    operation=ConfigOperation.DELETE
                ))
            
            # 重置配置
            new_data = deepcopy(new_config) if new_config else {}
            self._data = new_data
            
            # 通知所有删除和新配置项
            for event in delete_events:
                self._notify_change(event)
            
            for key, value in self._data.items():
                self._notify_change(ConfigChangeEvent(
                    key=key,
                    old_value=None,
                    new_value=value,
                    operation=ConfigOperation.SET
                ))
    
    def to_dict(self) -> Dict[str, Any]:
        """获取所有配置的深拷贝"""
        with self._lock:
            return deepcopy(self._data)
    
    def save(self, filename: Optional[str] = None, format: str = 'json') -> bool:
        """
        保存配置到文件
        
        参数:
            filename: 文件名 (可选，使用默认配置目录)
            format: 文件格式 ('json', 'yaml')
            
        返回:
            True 保存成功, False 保存失败
        """
        if filename is None and self._config_dir is None:
            raise ConfigError("未指定文件名且未设置配置目录")
        
        filepath = Path(filename) if filename else self._config_dir / f"config.{format}"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with filepath.open('w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                elif format == 'yaml':
                    import yaml
                    yaml.safe_dump(self.to_dict(), f, allow_unicode=True)
                else:
                    raise ConfigError(f"不支持的格式: {format}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}", exc_info=True)
            return False
    
    @classmethod
    def load(
        cls,
        filename: str,
        validators: Optional[Dict[str, ConfigValidator]] = None,
        config_dir: Optional[Union[str, Path]] = None,
        env_prefix: Optional[str] = None
    ) -> 'Config':
        """
        从文件加载配置
        
        参数:
            filename: 文件名
            validators: 配置验证器
            config_dir: 配置目录
            env_prefix: 环境变量前缀
            
        返回:
            加载的 Config 实例
            
        异常:
            ConfigError: 加载失败
        """
        filepath = Path(filename)
        if not filepath.is_absolute() and config_dir is not None:
            filepath = Path(config_dir) / filename
        
        try:
            with filepath.open('r', encoding='utf-8') as f:
                if filepath.suffix.lower() == '.json':
                    data = json.load(f)
                elif filepath.suffix.lower() in ('.yaml', '.yml'):
                    import yaml
                    data = yaml.safe_load(f)
                else:
                    raise ConfigError(f"不支持的文件格式: {filepath.suffix}")
                
                return cls(
                    initial_config=data,
                    validators=validators,
                    config_dir=config_dir,
                    env_prefix=env_prefix
                )
        except Exception as e:
            raise ConfigError(f"加载配置失败: {e}") from e
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        if not self._env_prefix:
            return
        
        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                config_key = key[len(self._env_prefix):].lower()
                try:
                    # 尝试解析JSON格式的环境变量
                    parsed_value = json.loads(value)
                    self._data[config_key] = parsed_value
                except json.JSONDecodeError:
                    # 普通字符串值
                    self._data[config_key] = value

    def register_validator(self, key: str, validator: ConfigValidator):
        """注册配置验证器"""
        with self._lock:
            self._validators[key] = validator
    
    def unregister_validator(self, key: str):
        """移除配置验证器"""
        with self._lock:
            if key in self._validators:
                del self._validators[key]
    
    def get_validator(self, key: str) -> Optional[ConfigValidator]:
        """获取配置验证器"""
        with self._lock:
            return self._validators.get(key)
    
    def validate_all(self) -> Dict[str, Union[Any, Exception]]:
        """验证所有配置项，返回验证结果字典"""
        results = {}
        with self._lock:
            for key, validator in self._validators.items():
                if key in self._data:
                    try:
                        results[key] = validator.validate(self._data[key])
                    except Exception as e:
                        results[key] = e
        return results