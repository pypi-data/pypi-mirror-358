"""
装饰器工具集，包含函数调用信息记录、弃用标记、重试机制和频率限制等功能。
"""

import functools
import warnings
import inspect
import time
import logging
import sys
import threading
import asyncio
from typing import Optional, Callable, Any, TypeVar, Union, Tuple
from pathlib import Path

T = TypeVar('T')
FuncType = Callable[..., T]
F = TypeVar('F', bound=FuncType[Any])


def info(
    func: Optional[F] = None,
    *,
    show_args: bool = False,
    show_kwargs: bool = False,
    show_return: bool = False,
    show_time: bool = False,
    log_file: Optional[Union[str, Path]] = None,
    indent: int = 0,
    log_level: int = logging.INFO,
) -> Union[F, Callable[[F], F]]:
    """
    装饰器：输出函数的详细调用信息
    
    参数:
        func: 被装饰的函数(自动传入，无需手动指定)
        show_args: 是否显示位置参数，默认False
        show_kwargs: 是否显示关键字参数，默认False
        show_return: 是否显示返回值，默认False
        show_time: 是否显示执行时间，默认False
        log_file: 日志文件路径，不指定则输出到stdout
        indent: 缩进空格数，用于嵌套调用时格式化输出
        log_level: 日志级别，默认为logging.INFO
        
    返回:
        包装后的函数，调用时会输出详细信息
    """
    def setup_logger() -> logging.Logger:
        """配置并返回logger实例"""
        logger = logging.getLogger(f"func_logger.{indent}")
        if logger.handlers:
            return logger
            
        logger.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        if log_file:
            handler = logging.FileHandler(log_file, encoding='utf-8')
        else:
            handler = logging.StreamHandler(sys.stdout)
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
        return logger

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = setup_logger()
            indent_str = ' ' * indent
            sig = inspect.signature(f)
            
            log_lines = [f"{indent_str}┌── 调用函数: {f.__name__}"]
            
            if show_args and args:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                arg_details = [
                    f"{name}={repr(value)}" 
                    for name, value in bound_args.arguments.items()
                    if name in sig.parameters and 
                    name not in kwargs and
                    (len(args) > list(sig.parameters.keys()).index(name))
                ]
                if arg_details:
                    log_lines.append(f"{indent_str}├── 位置参数: {', '.join(arg_details)}")
            
            if show_kwargs and kwargs:
                kwargs_details = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                log_lines.append(f"{indent_str}├── 关键字参数: {', '.join(kwargs_details)}")
            
            start_time = time.perf_counter()
            result = f(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            
            if show_return:
                log_lines.append(f"{indent_str}├── 返回值: {repr(result)}")
            
            if show_time:
                log_lines.append(f"{indent_str}└── 执行时间: {elapsed:.6f}秒")
            else:
                log_lines[-1] = log_lines[-1].replace('├──', '└──')
            
            logger.log(log_level, "\n".join(log_lines))
            return result

        @functools.wraps(f)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = setup_logger()
            indent_str = ' ' * indent
            sig = inspect.signature(f)
            
            log_lines = [f"{indent_str}┌── 调用异步函数: {f.__name__}"]
            
            if show_args and args:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                arg_details = [
                    f"{name}={repr(value)}"
                    for name, value in bound_args.arguments.items()
                    if name in sig.parameters and
                    name not in kwargs and
                    (len(args) > list(sig.parameters.keys()).index(name))
                ]
                if arg_details:
                    log_lines.append(f"{indent_str}├── 位置参数: {', '.join(arg_details)}")
            
            if show_kwargs and kwargs:
                kwargs_details = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                log_lines.append(f"{indent_str}├── 关键字参数: {', '.join(kwargs_details)}")
            
            start_time = time.perf_counter()
            result = await f(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            
            if show_return:
                log_lines.append(f"{indent_str}├── 返回值: {repr(result)}")
            
            if show_time:
                log_lines.append(f"{indent_str}└── 执行时间: {elapsed:.6f}秒")
            else:
                log_lines[-1] = log_lines[-1].replace('├──', '└──')
            
            logger.log(log_level, "\n".join(log_lines))
            return result

        return async_wrapper if inspect.iscoroutinefunction(f) else sync_wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def deprecated_func(
    func: Optional[F] = None,
    *,
    reason: Optional[str] = None,
    version: Optional[str] = None,
    alternative: Optional[str] = None,
    since: Optional[str] = None,
) -> Union[F, Callable[[F], F]]:
    """
    装饰器：标记函数已弃用，并在调用时发出警告
    
    参数:
        func: 被装饰的函数(自动传入，无需手动指定)
        reason: 弃用的原因说明
        version: 计划移除的版本号
        alternative: 推荐的替代函数或方法
        since: 从哪个版本开始弃用
        
    返回:
        包装后的函数，调用时会发出弃用警告
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            message_parts = [f"函数 {f.__name__} 已被弃用"]
            
            if since:
                message_parts.append(f"(自版本 {since})")
            
            if reason:
                message_parts.append(f"，原因: {reason}")
            
            if version:
                message_parts.append(f"，将在 {version} 版本中移除")
            
            if alternative:
                message_parts.append(f"，请使用 {alternative} 替代")
            
            message = "".join(message_parts)
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return f(*args, **kwargs)

        @functools.wraps(f)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            message = (
                f"异步函数 {f.__name__} 已被弃用"
                + (f"(自版本 {since})" if since else "")
                + (f"，原因: {reason}" if reason else "")
                + (f"，将在 {version} 版本中移除" if version else "")
                + (f"，请使用 {alternative} 替代" if alternative else "")
            )
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return await f(*args, **kwargs)

        wrapper = async_wrapper if inspect.iscoroutinefunction(f) else sync_wrapper
        
        wrapper._is_deprecated = True  # type: ignore
        wrapper._deprecation_info = {  # type: ignore
            'reason': reason,
            'version': version,
            'alternative': alternative,
            'since': since,
        }
        
        return wrapper  # type: ignore

    if func is None:
        return decorator
    else:
        return decorator(func)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Tuple[Exception], Exception] = Exception,
    logger: Optional[logging.Logger] = None,
):
    """
    装饰器：函数执行失败时自动重试
    
    参数:
        max_attempts: 最大尝试次数 (默认: 3)
        delay: 初始延迟时间(秒) (默认: 1.0)
        backoff: 延迟时间倍增系数 (默认: 2.0)
        exceptions: 需要捕获的异常类型 (默认: Exception)
        logger: 自定义logger (默认: 使用print)
        
    返回:
        包装后的函数
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                        
                    msg = (f"函数 {f.__name__} 第 {attempt} 次失败，"
                          f"{current_delay:.1f}秒后重试... 错误: {str(e)}")
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                        
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise RuntimeError(f"函数 {f.__name__} 在 {max_attempts} 次尝试后仍失败") from last_exception

        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                        
                    msg = (f"异步函数 {f.__name__} 第 {attempt} 次失败，"
                          f"{current_delay:.1f}秒后重试... 错误: {str(e)}")
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                        
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise RuntimeError(f"异步函数 {f.__name__} 在 {max_attempts} 次尝试后仍失败") from last_exception

        return async_wrapper if inspect.iscoroutinefunction(f) else sync_wrapper
    return decorator


def rate_limited(
    calls: int = 1,
    period: float = 1.0,
    raise_on_limit: bool = False
):
    """
    装饰器：限制函数调用频率
    
    参数:
        calls: 时间段内允许的最大调用次数 (默认: 1)
        period: 时间段的长度(秒) (默认: 1.0)
        raise_on_limit: 超出限制时是否抛出异常 (默认: False, 会阻塞等待)
        
    返回:
        包装后的函数
    """
    def decorator(f: F) -> F:
        call_times = []
        lock = threading.Lock()

        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            nonlocal call_times
            
            with lock:
                now = time.time()
                call_times = [t for t in call_times if t > now - period]
                
                if len(call_times) >= calls:
                    if raise_on_limit:
                        raise RuntimeError(f"调用频率限制: {calls}次/{period}秒")
                    else:
                        oldest = call_times[0]
                        wait_time = max(0, oldest + period - now)
                        if wait_time > 0:
                            time.sleep(wait_time)
                
                call_times.append(time.time())
                return f(*args, **kwargs)

        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            nonlocal call_times
            
            with lock:
                now = time.time()
                call_times = [t for t in call_times if t > now - period]
                
                if len(call_times) >= calls:
                    if raise_on_limit:
                        raise RuntimeError(f"调用频率限制: {calls}次/{period}秒")
                    else:
                        oldest = call_times[0]
                        wait_time = max(0, oldest + period - now)
                        if wait_time > 0:
                            await asyncio.sleep(wait_time)
                
                call_times.append(time.time())
                return await f(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(f) else sync_wrapper
    return decorator


def timeout(
    seconds: float,
    timeout_handler: Optional[Callable[[], Any]] = None,
    exception: type = TimeoutError
):
    """
    装饰器：为函数添加执行超时限制
    
    参数:
        seconds: 超时时间(秒)
        timeout_handler: 超时时的处理函数 (默认: 抛出异常)
        exception: 超时时抛出的异常类型 (默认: TimeoutError)
        
    返回:
        包装后的函数
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs):
            result = None
            timed_out = False
            
            def worker():
                nonlocal result
                result = f(*args, **kwargs)
            
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                timed_out = True
                thread.join(0.1)
                
            if timed_out:
                if timeout_handler is not None:
                    return timeout_handler()
                raise exception(f"函数 {f.__name__} 执行超时 ({seconds}秒)")
            return result

        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    f(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                if timeout_handler is not None:
                    return timeout_handler()
                raise exception(f"异步函数 {f.__name__} 执行超时 ({seconds}秒)")

        return async_wrapper if inspect.iscoroutinefunction(f) else sync_wrapper
    return decorator