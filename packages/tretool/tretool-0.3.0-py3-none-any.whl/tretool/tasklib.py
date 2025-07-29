import os
import psutil
import time
import signal
import subprocess
import threading
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable, Set, Tuple, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future
import logging
from logging.handlers import RotatingFileHandler
import platform
import json
from collections import defaultdict

# 日志配置
def setup_logging(log_file: str = 'process_manager.log', max_size: int = 10):
    """配置日志记录"""
    logger = logging.getLogger('ProcessManager')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器（轮转日志）
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_size*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

logger = setup_logging()

class ProcessStatus(Enum):
    """进程状态枚举"""
    RUNNING = auto()
    STOPPED = auto()
    ZOMBIE = auto()
    UNKNOWN = auto()
    IDLE = auto()
    SLEEPING = auto()
    TRACING_STOP = auto()

@dataclass
class ProcessInfo:
    """进程信息数据类"""
    pid: int
    name: str
    status: ProcessStatus
    cpu_percent: float
    memory_mb: float
    create_time: float
    cmdline: List[str]
    threads: int
    username: str
    connections: List[dict]
    open_files: List[str]
    children: List['ProcessInfo'] = field(default_factory=list)
    exit_code: Optional[int] = None
    cpu_times: Optional[dict] = None
    io_counters: Optional[dict] = None
    environ: Optional[dict] = None

class ProcessObserver(ABC):
    """观察者抽象基类"""
    
    @abstractmethod
    def on_process_start(self, pid: int, info: ProcessInfo):
        """进程启动回调"""
        pass

    @abstractmethod
    def on_process_stop(self, pid: int, info: ProcessInfo):
        """进程停止回调"""
        pass

    @abstractmethod
    def on_process_update(self, pid: int, info: ProcessInfo):
        """进程状态更新回调"""
        pass

    @abstractmethod
    def on_resource_alert(self, pid: int, alert_type: str, info: ProcessInfo):
        """资源警报回调"""
        pass

class LoggingObserver(ProcessObserver):
    """日志记录观察者实现"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('ProcessObserver')
        
    def on_process_start(self, pid: int, info: ProcessInfo):
        self.logger.info(
            f"Process started - PID: {pid}, "
            f"Name: {info.name}, "
            f"User: {info.username}, "
            f"CMD: {' '.join(info.cmdline[:1])}..."
        )
        
    def on_process_stop(self, pid: int, info: ProcessInfo):
        exit_code = info.exit_code if info.exit_code is not None else 'N/A'
        self.logger.info(
            f"Process stopped - PID: {pid}, "
            f"ExitCode: {exit_code}, "
            f"Duration: {time.time() - info.create_time:.2f}s"
        )
        
    def on_process_update(self, pid: int, info: ProcessInfo):
        self.logger.debug(
            f"Process update - PID: {pid}, "
            f"CPU: {info.cpu_percent:.1f}%, "
            f"MEM: {info.memory_mb:.1f}MB, "
            f"Threads: {info.threads}"
        )
        
    def on_resource_alert(self, pid: int, alert_type: str, info: ProcessInfo):
        alert_msg = {
            'high_cpu': f"High CPU usage ({info.cpu_percent:.1f}%)",
            'high_memory': f"High memory usage ({info.memory_mb:.1f}MB)",
            'many_threads': f"Too many threads ({info.threads})",
            'many_connections': f"Too many connections ({len(info.connections)})",
            'many_files': f"Too many open files ({len(info.open_files)})"
        }.get(alert_type, alert_type)
        
        self.logger.warning(
            f"Resource alert - PID: {pid} {alert_msg}, "
            f"Name: {info.name}"
        )

class ResourceGuardObserver(ProcessObserver):
    """资源守护观察者（自动终止异常进程）"""
    
    def __init__(self, 
                 max_cpu: float = 90.0, 
                 max_memory_mb: float = 1024,
                 max_threads: int = 100,
                 max_connections: int = 50,
                 max_files: int = 500,
                 max_duration: float = 3600):
        self.max_cpu = max_cpu
        self.max_memory = max_memory_mb
        self.max_threads = max_threads
        self.max_connections = max_connections
        self.max_files = max_files
        self.max_duration = max_duration
        self.violations = defaultdict(dict)
        
    def on_process_start(self, pid: int, info: ProcessInfo):
        self.violations[pid] = {
            'start_time': time.time(),
            'high_cpu_count': 0,
            'high_memory_count': 0,
            'high_threads_count': 0,
            'high_connections_count': 0,
            'high_files_count': 0
        }
        
    def on_process_stop(self, pid: int, info: ProcessInfo):
        self.violations.pop(pid, None)
        
    def on_process_update(self, pid: int, info: ProcessInfo):
        if pid not in self.violations:
            return
            
        violations = self.violations[pid]
        
        # 检查运行时长
        if time.time() - info.create_time > self.max_duration:
            self._terminate(pid, reason="Timeout exceeded")
            return
            
        # 检查资源使用
        if info.cpu_percent > self.max_cpu:
            violations['high_cpu_count'] += 1
        else:
            violations['high_cpu_count'] = 0
            
        if info.memory_mb > self.max_memory:
            violations['high_memory_count'] += 1
        else:
            violations['high_memory_count'] = 0
            
        if info.threads > self.max_threads:
            violations['high_threads_count'] += 1
        else:
            violations['high_threads_count'] = 0
            
        if len(info.connections) > self.max_connections:
            violations['high_connections_count'] += 1
        else:
            violations['high_connections_count'] = 0
            
        if len(info.open_files) > self.max_files:
            violations['high_files_count'] += 1
        else:
            violations['high_files_count'] = 0
            
        # 连续3次超标则终止
        if any(count >= 3 for count in violations.values() if isinstance(count, int)):
            reason = ", ".join(
                f"{k.replace('_count', '')}" 
                for k, v in violations.items() 
                if isinstance(v, int) and v >= 3
            )
            self._terminate(pid, reason=f"Resource violation: {reason}")
    
    def on_resource_alert(self, pid: int, alert_type: str, info: ProcessInfo):
        pass  # 已在update中处理
    
    def _terminate(self, pid: int, reason: str):
        try:
            os.kill(pid, signal.SIGTERM)
            logger.warning(f"Terminated process {pid}, reason: {reason}")
            time.sleep(1)
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGKILL)
                logger.warning(f"Force killed process {pid}")
        except ProcessLookupError:
            pass
        finally:
            self.violations.pop(pid, None)

class ProcessError(Exception):
    """进程操作异常基类"""
    pass

class ProcessNotFoundError(ProcessError):
    """进程未找到异常"""
    pass

class ProcessPermissionError(ProcessError):
    """进程权限异常"""
    pass

class ProcessManager:
    """进程管理器主类"""
    
    def __init__(self, monitor_interval: float = 1.0):
        self._observers: List[ProcessObserver] = []
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_interval = monitor_interval
        self._should_monitor = False
        self._process_cache: Dict[int, ProcessInfo] = {}
        self._executor = ThreadPoolExecutor(max_workers=8)
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._system = platform.system()
        
        # 自动添加日志观察者
        self.add_observer(LoggingObserver(logger))

    def __enter__(self):
        """上下文管理器入口"""
        self.monitor_start(self._monitor_interval)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.monitor_stop()
        self._executor.shutdown(wait=True)
        
    def start_process(
        self,
        command: Union[str, List[str]],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        shell: bool = False,
        capture_output: bool = False,
        **kwargs
    ) -> ProcessInfo:
        """
        启动新进程
        
        参数:
            command: 命令字符串或列表
            cwd: 工作目录
            env: 环境变量
            shell: 是否使用shell执行
            capture_output: 是否捕获输出
            kwargs: 其他subprocess.Popen参数
            
        返回:
            ProcessInfo对象
            
        抛出:
            ProcessError: 启动失败时
        """
        try:
            if isinstance(command, str) and not shell:
                command = [cmd.strip() for cmd in command.split() if cmd.strip()]
                
            stdout = subprocess.PIPE if capture_output else None
            stderr = subprocess.PIPE if capture_output else None
            
            proc = psutil.Popen(
                command,
                cwd=cwd,
                env=env or os.environ,
                stdout=stdout,
                stderr=stderr,
                shell=shell,
                **kwargs
            )
            
            info = self._get_process_info(proc.pid)
            self._notify_observers('start', proc.pid, info)
            
            # 启动线程监控子进程输出
            if capture_output:
                self._executor.submit(self._capture_output, proc)
                
            return info
        except Exception as e:
            raise ProcessError(f"Failed to start process: {str(e)}")

    def stop_process(
        self,
        pid: int,
        timeout: int = 5,
        force: bool = False,
        kill_children: bool = True
    ) -> bool:
        """
        停止指定进程
        
        参数:
            pid: 进程ID
            timeout: 等待超时(秒)
            force: 是否强制杀死
            kill_children: 是否杀死子进程
            
        返回:
            是否成功停止
            
        抛出:
            ProcessNotFoundError: 进程不存在时
            ProcessError: 其他错误
        """
        try:
            proc = psutil.Process(pid)
            info = self._get_process_info(pid)
            
            if kill_children:
                for child in proc.children(recursive=True):
                    try:
                        if force:
                            child.kill()
                        else:
                            child.terminate()
                    except psutil.NoSuchProcess:
                        continue
            
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            try:
                proc.wait(timeout=timeout)
            except psutil.TimeoutExpired:
                if force:
                    return False
                try:
                    proc.kill()
                    proc.wait(timeout=1)
                except:
                    return False
            
            self._notify_observers('stop', pid, info)
            return True
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process {pid} not found")
        except psutil.AccessDenied:
            raise ProcessPermissionError(f"No permission to access process {pid}")
        except Exception as e:
            raise ProcessError(f"Failed to stop process {pid}: {str(e)}")

    def list_processes(
        self,
        name_filter: Optional[str] = None,
        user_filter: Optional[str] = None,
        include_children: bool = False,
        only_running: bool = True
    ) -> List[ProcessInfo]:
        """
        获取进程列表
        
        参数:
            name_filter: 进程名过滤
            user_filter: 用户名过滤
            include_children: 是否包含子进程
            only_running: 是否只返回运行中的进程
            
        返回:
            进程信息列表
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
            try:
                if only_running and proc.info['status'] != psutil.STATUS_RUNNING:
                    continue
                    
                if name_filter and name_filter.lower() not in proc.info['name'].lower():
                    continue
                    
                if user_filter and user_filter.lower() != proc.info['username'].lower():
                    continue
                
                info = self._get_process_info(proc.info['pid'])
                processes.append(info)
                
                if include_children:
                    for child in proc.children(recursive=True):
                        try:
                            processes.append(self._get_process_info(child.pid))
                        except psutil.NoSuchProcess:
                            continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def get_process_info(self, pid: int) -> ProcessInfo:
        """
        获取指定进程详细信息
        
        参数:
            pid: 进程ID
            
        返回:
            ProcessInfo对象
            
        抛出:
            ProcessNotFoundError: 进程不存在时
        """
        try:
            return self._get_process_info(pid)
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process {pid} not found")

    def monitor_start(self, interval: float = None) -> None:
        """启动后台监控"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        
        if interval is not None:
            self._monitor_interval = interval
        
        self._should_monitor = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ProcessMonitor"
        )
        self._monitor_thread.start()
        logger.info("Process monitor started")

    def monitor_stop(self) -> None:
        """停止监控"""
        if not self._should_monitor:
            return
            
        self._should_monitor = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            logger.info("Process monitor stopped")

    def add_observer(self, observer: ProcessObserver) -> None:
        """添加观察者"""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
                logger.debug(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: ProcessObserver) -> None:
        """移除观察者"""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                logger.debug(f"Removed observer: {observer.__class__.__name__}")

    def get_stats(self) -> dict:
        """获取管理器统计信息"""
        return {
            "uptime": time.time() - self._start_time,
            "monitoring": self._should_monitor,
            "monitor_interval": self._monitor_interval,
            "observed_processes": len(self._process_cache),
            "observers": len(self._observers)
        }

    def _monitor_loop(self) -> None:
        """监控主循环"""
        logger.info("Monitor loop started")
        while self._should_monitor:
            start_time = time.time()
            current_processes = {}
            
            try:
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    try:
                        pid = proc.info['pid']
                        info = self._get_process_info(pid)
                        current_processes[pid] = info
                        
                        # 检查资源使用情况
                        self._check_resources(pid, info)
                        
                        # 处理新增或状态变化的进程
                        if pid not in self._process_cache:
                            self._notify_observers('start', pid, info)
                        elif info.status != self._process_cache[pid].status:
                            self._notify_observers('update', pid, info)
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # 处理已退出的进程
                for pid in set(self._process_cache) - set(current_processes):
                    info = self._process_cache[pid]
                    info.status = ProcessStatus.STOPPED
                    self._notify_observers('stop', pid, info)
                
                self._process_cache = current_processes
                
            except Exception as e:
                logger.error(f"Monitor loop error: {str(e)}", exc_info=True)
            
            # 精确控制间隔时间
            elapsed = time.time() - start_time
            sleep_time = max(0, self._monitor_interval - elapsed)
            time.sleep(sleep_time)

    def _get_process_info(self, pid: int) -> ProcessInfo:
        """获取进程详细信息"""
        proc = psutil.Process(pid)
        with proc.oneshot():
            mem_info = proc.memory_info()
            status = self._convert_status(proc.status())
            
            try:
                connections = proc.connections()
            except (psutil.AccessDenied, psutil.Error):
                connections = []
                
            try:
                open_files = [f.path for f in proc.open_files()]
            except (psutil.AccessDenied, psutil.Error):
                open_files = []
                
            try:
                cpu_times = proc.cpu_times()._asdict()
            except (psutil.AccessDenied, psutil.Error):
                cpu_times = None
                
            try:
                io_counters = proc.io_counters()._asdict()
            except (psutil.AccessDenied, psutil.Error):
                io_counters = None
                
            try:
                environ = proc.environ()
            except (psutil.AccessDenied, psutil.Error):
                environ = None
                
            children = []
            try:
                for child in proc.children(recursive=False):
                    try:
                        children.append(self._get_process_info(child.pid))
                    except psutil.NoSuchProcess:
                        continue
            except psutil.AccessDenied:
                pass
                
            return ProcessInfo(
                pid=pid,
                name=proc.name(),
                status=status,
                cpu_percent=proc.cpu_percent(),
                memory_mb=mem_info.rss / (1024 * 1024),
                create_time=proc.create_time(),
                cmdline=proc.cmdline(),
                threads=proc.num_threads(),
                username=proc.username(),
                connections=connections,
                open_files=open_files,
                children=children,
                exit_code=proc.returncode if status == ProcessStatus.STOPPED else None,
                cpu_times=cpu_times,
                io_counters=io_counters,
                environ=environ
            )

    def _check_resources(self, pid: int, info: ProcessInfo) -> None:
        """检查资源使用情况并触发警报"""
        thresholds = [
            ('high_cpu', info.cpu_percent > 90),
            ('high_memory', info.memory_mb > 1024),
            ('many_threads', info.threads > 100),
            ('many_connections', len(info.connections) > 50),
            ('many_files', len(info.open_files) > 500)
        ]
        
        for alert_type, condition in thresholds:
            if condition:
                self._notify_observers('alert', pid, info, alert_type)

    def _notify_observers(self, event_type: str, pid: int, info: ProcessInfo, alert_type: str = None):
        """通知所有观察者"""
        def notify_task():
            with self._lock:
                observers = self._observers.copy()
            
            for observer in observers:
                try:
                    if event_type == 'start':
                        observer.on_process_start(pid, info)
                    elif event_type == 'stop':
                        observer.on_process_stop(pid, info)
                    elif event_type == 'update':
                        observer.on_process_update(pid, info)
                    elif event_type == 'alert':
                        observer.on_resource_alert(pid, alert_type, info)
                except Exception as e:
                    logger.error(f"Observer notification failed: {str(e)}", exc_info=True)
        
        self._executor.submit(notify_task)

    def _capture_output(self, proc: psutil.Popen):
        """捕获进程输出"""
        def reader(stream, callback):
            try:
                for line in iter(stream.readline, b''):
                    if line:
                        callback(line.decode('utf-8', errors='replace').strip())
            except ValueError:
                pass  # Stream closed
        
        def stdout_callback(line):
            logger.info(f"Process {proc.pid} stdout: {line}")
            
        def stderr_callback(line):
            logger.warning(f"Process {proc.pid} stderr: {line}")
        
        stdout_thread = threading.Thread(
            target=reader,
            args=(proc.stdout, stdout_callback),
            daemon=True
        )
        
        stderr_thread = threading.Thread(
            target=reader,
            args=(proc.stderr, stderr_callback),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        stdout_thread.join()
        stderr_thread.join()

    def _convert_status(self, status: str) -> ProcessStatus:
        """转换状态字符串为枚举"""
        status = status.upper()
        status_map = {
            "RUNNING": ProcessStatus.RUNNING,
            "SLEEPING": ProcessStatus.SLEEPING,
            "IDLE": ProcessStatus.IDLE,
            "STOPPED": ProcessStatus.STOPPED,
            "TRACING_STOP": ProcessStatus.TRACING_STOP,
            "ZOMBIE": ProcessStatus.ZOMBIE
        }
        return status_map.get(status, ProcessStatus.UNKNOWN)

# 示例用法
if __name__ == "__main__":
    # 创建进程管理器
    with ProcessManager(monitor_interval=2.0) as manager:
        # 添加资源守护观察者
        guard = ResourceGuardObserver(
            max_cpu=80.0,
            max_memory_mb=512,
            max_threads=50,
            max_duration=30
        )
        manager.add_observer(guard)
        
        # 启动一个进程
        try:
            print("Starting a process...")
            proc_info = manager.start_process(
                ["python", "-c", "while True: pass"],  # 模拟CPU密集型进程
                capture_output=True
            )
            print(f"Started process PID: {proc_info.pid}")
            
            # 查看进程列表
            print("\nProcess list:")
            for p in manager.list_processes(only_running=True)[:5]:
                print(f"PID: {p.pid}, Name: {p.name}, CPU: {p.cpu_percent}%")
            
            # 让监控运行一段时间
            print("\nMonitoring for 10 seconds...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            # 停止所有我们启动的进程
            for p in manager.list_processes():
                if "python" in p.name.lower():
                    try:
                        print(f"Stopping process {p.pid}...")
                        manager.stop_process(p.pid)
                    except Exception as e:
                        print(f"Error stopping process {p.pid}: {str(e)}")