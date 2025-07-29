import sys
import os
import datetime
import traceback
import threading
import gzip
import json
from typing import (
    Any, Tuple, List, Optional, Union, TextIO, Callable, Dict,
    TypeVar, Generic, Type
)
from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from queue import Queue, Empty, Full
from collections import deque
import inspect
import socket
import uuid

# 类型变量
T = TypeVar('T')

class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    AUDIT = auto()  # 审计日志
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """从字符串转换日志级别"""
        try:
            return cls[level_str.upper()]
        except KeyError:
            raise ValueError(f"无效的日志级别: {level_str}") from None

@dataclass
class LogRecord:
    """日志记录数据结构"""
    level: LogLevel
    message: str
    timestamp: str
    logger_name: str
    user: Optional[str] = None
    module: Optional[str] = None
    func_name: Optional[str] = None
    lineno: Optional[int] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    hostname: Optional[str] = None
    request_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    exc_info: Optional[Tuple[Type[BaseException], BaseException, Any]] = None

class LogHandler(ABC):
    """日志处理器抽象基类"""
    
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level
        self._lock = threading.Lock()
        self._formatter = self.default_formatter
    
    @abstractmethod
    def emit(self, record: LogRecord) -> None:
        """处理日志记录"""
        pass
    
    def set_level(self, level: LogLevel) -> None:
        """设置处理器级别"""
        with self._lock:
            self.level = level
    
    def filter(self, record: LogRecord) -> bool:
        """过滤日志记录"""
        return record.level.value >= self.level.value
    
    @staticmethod
    def default_formatter(record: LogRecord) -> str:
        """默认日志格式化方法"""
        parts = [
            f"[{record.timestamp}]",
            f"({record.level.name})",
            f"{record.logger_name}:",
        ]
        
        if record.user:
            parts.append(f"user={record.user}")
            
        if record.module:
            parts.append(f"module={record.module}")
            
        if record.func_name:
            parts.append(f"func={record.func_name}")
            
        if record.lineno:
            parts.append(f"line={record.lineno}")
            
        parts.append(record.message)
        
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            parts.append('\n' + ''.join(tb_lines).strip())
        
        return ' '.join(parts)
    
    def format(self, record: LogRecord) -> str:
        """格式化日志记录"""
        return self.default_formatter(record)
    
    def close(self) -> None:
        """关闭处理器"""
        pass

class StreamHandler(LogHandler):
    """流处理器（控制台输出）"""
    
    def __init__(
        self,
        stream: TextIO = sys.stdout,
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[Callable[[LogRecord], str]] = None
    ):
        super().__init__(level)
        self.stream = stream
        if formatter is not None:
            self._formatter = formatter
    
    def emit(self, record: LogRecord) -> None:
        """输出日志到流"""
        if not self.filter(record):
            return
            
        formatted = self.format(record)
        
        with self._lock:
            try:
                self.stream.write(formatted + '\n')
                self.stream.flush()
            except (ValueError, AttributeError):
                # 流已关闭
                pass
    
    def close(self) -> None:
        """关闭流"""
        if hasattr(self.stream, 'close') and self.stream not in (sys.stdout, sys.stderr):
            self.stream.close()

class FileHandler(LogHandler):
    """文件处理器"""
    
    def __init__(
        self,
        filename: Union[str, Path],
        mode: str = 'a',
        encoding: str = 'utf-8',
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[Callable[[LogRecord], str]] = None,
        delay: bool = False
    ):
        super().__init__(level)
        self.filename = Path(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        self._file: Optional[TextIO] = None
        if formatter is not None:
            self._formatter = formatter
        
        if not delay:
            self._open_file()
    
    def _open_file(self) -> None:
        """打开日志文件"""
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filename, self.mode, encoding=self.encoding)
    
    def emit(self, record: LogRecord) -> None:
        """写入日志到文件"""
        if not self.filter(record):
            return
            
        if self._file is None and self.delay:
            self._open_file()
        
        formatted = self.format(record)
        
        with self._lock:
            if self._file is not None:
                try:
                    self._file.write(formatted + '\n')
                    self._file.flush()
                except (OSError, ValueError):
                    # 文件已关闭或不可写
                    self._file = None
    
    def close(self) -> None:
        """关闭文件"""
        if self._file is not None:
            with self._lock:
                if self._file is not None:
                    self._file.close()
                    self._file = None

class RotatingFileHandler(FileHandler):
    """滚动文件处理器"""
    
    def __init__(
        self,
        filename: Union[str, Path],
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        mode: str = 'a',
        encoding: str = 'utf-8',
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[Callable[[LogRecord], str]] = None,
        delay: bool = False
    ):
        super().__init__(filename, mode, encoding, level, formatter, delay)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
    
    def emit(self, record: LogRecord) -> None:
        """处理日志记录，必要时滚动文件"""
        if not self.filter(record):
            return
            
        if self._file is None and self.delay:
            self._open_file()
        
        formatted = self.format(record)
        
        with self._lock:
            if self._file is not None:
                try:
                    # 检查是否需要滚动
                    if self._file.tell() + len(formatted) > self.max_bytes:
                        self._do_rollover()
                    
                    self._file.write(formatted + '\n')
                    self._file.flush()
                except (OSError, ValueError):
                    # 文件已关闭或不可写
                    self._file = None
    
    def _do_rollover(self) -> None:
        """执行文件滚动"""
        if self._file is not None:
            self._file.close()
            self._file = None
        
        # 重命名现有日志文件
        for i in range(self.backup_count - 1, 0, -1):
            src = self.filename.with_suffix(f'.{i}')
            dst = self.filename.with_suffix(f'.{i+1}')
            if src.exists():
                if dst.exists():
                    dst.unlink()
                src.rename(dst)
        
        # 重命名主日志文件
        dst = self.filename.with_suffix('.1')
        if dst.exists():
            dst.unlink()
        if self.filename.exists():
            self.filename.rename(dst)
        
        # 重新打开主日志文件
        self._open_file()

class JSONFormatter:
    """JSON格式化器"""
    
    def __call__(self, record: LogRecord) -> str:
        """将日志记录转换为JSON字符串"""
        record_dict = asdict(record)
        record_dict['level'] = record.level.name
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            record_dict['exception'] = {
                'type': exc_type.__name__,
                'message': str(exc_value),
                'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
            }
        return json.dumps(record_dict, ensure_ascii=False)

class Logger:
    """
    终极版日志记录器
    
    特性:
    - 多级别日志记录
    - 多处理器支持
    - 线程安全
    - 异步日志支持
    - 上下文信息记录
    - 结构化日志(JSON)
    - 日志轮转
    - 审计日志
    """
    
    _loggers: Dict[str, 'Logger'] = {}
    _lock = threading.Lock()
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        handlers: Optional[List[LogHandler]] = None,
        propagate: bool = True,
        async_mode: bool = False,
        queue_size: int = 1000
    ):
        """
        初始化日志记录器
        
        参数:
            name: 日志器名称
            level: 日志级别阈值
            handlers: 日志处理器列表
            propagate: 是否传播到父日志器
            async_mode: 是否启用异步模式
            queue_size: 异步队列大小
        """
        self.name = name
        self.level = level
        self.handlers = handlers or []
        self.propagate = propagate
        self.parent: Optional['Logger'] = None
        self._async_mode = async_mode
        self._queue: Optional[Queue] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        if async_mode:
            self._init_async_logging(queue_size)
    
    def _init_async_logging(self, queue_size: int) -> None:
        """初始化异步日志记录"""
        self._queue = Queue(maxsize=queue_size)
        self._worker_thread = threading.Thread(
            target=self._process_log_records,
            name=f"Logger-{self.name}-Worker",
            daemon=True
        )
        self._worker_thread.start()
    
    def _process_log_records(self) -> None:
        """处理日志记录的线程函数"""
        while not self._stop_event.is_set():
            try:
                record = self._queue.get(timeout=0.1)
                self._handle_record(record)
            except Empty:
                continue
            except Exception:
                # 防止工作线程因异常退出
                continue
    
    def _handle_record(self, record: LogRecord) -> None:
        """处理日志记录"""
        for handler in self.handlers:
            try:
                handler.emit(record)
            except Exception:
                # 处理器错误不应中断日志系统
                continue
        
        # 传播到父日志器
        if self.propagate and self.parent is not None:
            self.parent._handle_record(record)
    
    def _make_record(
        self,
        level: LogLevel,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Tuple[Type[BaseException], BaseException, Any]] = None,
        stack_level: int = 1
    ) -> LogRecord:
        """创建日志记录对象"""
        # 获取调用者信息
        frame = inspect.currentframe()
        for _ in range(stack_level + 1):
            if frame is None:
                break
            frame = frame.f_back
        
        module = None
        func_name = None
        lineno = None
        
        if frame is not None:
            module = inspect.getmodule(frame)
            if module is not None:
                module = module.__name__
            func_name = frame.f_code.co_name
            lineno = frame.f_lineno
        
        # 获取进程和线程信息
        process_id = os.getpid()
        thread_id = threading.get_ident()
        
        # 获取主机名
        try:
            hostname = socket.gethostname()
        except:
            hostname = None
        
        return LogRecord(
            level=level,
            message=message,
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            logger_name=self.name,
            user=user,
            module=module,
            func_name=func_name,
            lineno=lineno,
            process_id=process_id,
            thread_id=thread_id,
            hostname=hostname,
            request_id=Logger.get_request_id(),
            extra=extra,
            exc_info=exc_info
        )
    
    @staticmethod
    def get_request_id() -> str:
        """获取当前请求ID（用于分布式追踪）"""
        # 可以从线程局部存储或上下文获取
        return str(uuid.uuid4())
    
    def add_handler(self, handler: LogHandler) -> None:
        """添加日志处理器"""
        with self._lock:
            self.handlers.append(handler)
    
    def remove_handler(self, handler: LogHandler) -> None:
        """移除日志处理器"""
        with self._lock:
            if handler in self.handlers:
                self.handlers.remove(handler)
    
    def set_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        with self._lock:
            self.level = level
    
    def log(
        self,
        level: LogLevel,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Tuple[Type[BaseException], BaseException, Any]] = None,
        stack_level: int = 1
    ) -> None:
        """记录日志"""
        if level.value < self.level.value:
            return
            
        record = self._make_record(level, message, user, extra, exc_info, stack_level + 1)
        
        if self._async_mode and self._queue is not None:
            try:
                self._queue.put_nowait(record)
            except Full:
                # 队列已满，同步处理
                self._handle_record(record)
        else:
            self._handle_record(record)
    
    def debug(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录DEBUG级别日志"""
        self.log(LogLevel.DEBUG, message, user, extra, None, stack_level + 1)
    
    def info(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录INFO级别日志"""
        self.log(LogLevel.INFO, message, user, extra, None, stack_level + 1)
    
    def warning(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录WARNING级别日志"""
        self.log(LogLevel.WARNING, message, user, extra, None, stack_level + 1)
    
    def error(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Tuple[Type[BaseException], BaseException, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录ERROR级别日志"""
        self.log(LogLevel.ERROR, message, user, extra, exc_info, stack_level + 1)
    
    def critical(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Tuple[Type[BaseException], BaseException, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录CRITICAL级别日志"""
        self.log(LogLevel.CRITICAL, message, user, extra, exc_info, stack_level + 1)
    
    def audit(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录审计日志"""
        self.log(LogLevel.AUDIT, message, user, extra, None, stack_level + 1)
    
    def exception(
        self,
        message: str,
        user: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_level: int = 0
    ) -> None:
        """记录当前异常"""
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            self.log(LogLevel.ERROR, message, user, extra, exc_info, stack_level + 1)
    
    def close(self) -> None:
        """关闭日志记录器"""
        if self._async_mode:
            self._stop_event.set()
            if self._worker_thread is not None:
                self._worker_thread.join(timeout=5)
            
            # 处理队列中剩余日志
            if self._queue is not None:
                while not self._queue.empty():
                    try:
                        record = self._queue.get_nowait()
                        self._handle_record(record)
                    except Empty:
                        break
        
        for handler in self.handlers:
            handler.close()
    
    @classmethod
    def get_logger(
        cls,
        name: str = 'root',
        level: Optional[LogLevel] = None,
        handlers: Optional[List[LogHandler]] = None,
        propagate: bool = True,
        async_mode: bool = False,
        queue_size: int = 1000
    ) -> 'Logger':
        """获取或创建日志记录器"""
        with cls._lock:
            if name in cls._loggers:
                logger = cls._loggers[name]
                # 更新配置
                if level is not None:
                    logger.set_level(level)
                if handlers is not None:
                    logger.handlers = handlers
                logger.propagate = propagate
                return logger
            else:
                # 创建层次结构
                parts = name.split('.')
                parent = None
                
                for i in range(1, len(parts)):
                    parent_name = '.'.join(parts[:i])
                    if parent_name not in cls._loggers:
                        cls._loggers[parent_name] = Logger(
                            name=parent_name,
                            level=LogLevel.INFO,
                            propagate=True
                        )
                
                if len(parts) > 1:
                    parent_name = '.'.join(parts[:-1])
                    parent = cls._loggers.get(parent_name)
                
                logger = Logger(
                    name=name,
                    level=level or LogLevel.INFO,
                    handlers=handlers,
                    propagate=propagate,
                    async_mode=async_mode,
                    queue_size=queue_size
                )
                logger.parent = parent
                cls._loggers[name] = logger
                return logger
    
    @classmethod
    def shutdown(cls) -> None:
        """关闭所有日志记录器"""
        with cls._lock:
            for logger in cls._loggers.values():
                logger.close()
            cls._loggers.clear()

# 全局默认日志记录器
_default_logger = Logger.get_logger('root')

# 便捷函数
def debug(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录DEBUG级别日志"""
    _default_logger.debug(message, user, kwargs)

def info(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录INFO级别日志"""
    _default_logger.info(message, user, kwargs)

def warning(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录WARNING级别日志"""
    _default_logger.warning(message, user, kwargs)

def error(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录ERROR级别日志"""
    _default_logger.error(message, user, kwargs)

def critical(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录CRITICAL级别日志"""
    _default_logger.critical(message, user, kwargs)

def audit(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录审计日志"""
    _default_logger.audit(message, user, kwargs)

def exception(message: str, user: Optional[str] = None, **kwargs) -> None:
    """记录当前异常"""
    _default_logger.exception(message, user, kwargs)

def get_logger(name: str = 'root', **kwargs) -> Logger:
    """获取命名的日志记录器"""
    return Logger.get_logger(name, **kwargs)

def setup_default_logger(
    level: Union[LogLevel, str] = LogLevel.INFO,
    filename: Optional[Union[str, Path]] = None,
    console: bool = True,
    json_format: bool = False,
    max_bytes: Optional[int] = None,
    backup_count: int = 5,
    async_mode: bool = False,
    queue_size: int = 1000
) -> None:
    """设置全局默认日志记录器"""
    global _default_logger
    
    if isinstance(level, str):
        level = LogLevel.from_string(level)
    
    handlers = []
    formatter = JSONFormatter() if json_format else None
    
    if console:
        handlers.append(StreamHandler(formatter=formatter))
    
    if filename is not None:
        if max_bytes is not None:
            handlers.append(
                RotatingFileHandler(
                    filename,
                    max_bytes=max_bytes,
                    backup_count=backup_count,
                    formatter=formatter
                )
            )
        else:
            handlers.append(FileHandler(filename, formatter=formatter))
    
    _default_logger = Logger.get_logger(
        'root',
        level=level,
        handlers=handlers,
        async_mode=async_mode,
        queue_size=queue_size
    )

def shutdown() -> None:
    """关闭日志系统"""
    Logger.shutdown()