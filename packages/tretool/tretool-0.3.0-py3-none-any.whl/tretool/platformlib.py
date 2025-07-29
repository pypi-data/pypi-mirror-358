import os
import sys
import ctypes
import platform
import time
import warnings
import threading
import subprocess
import re
import json
from typing import (Any, Dict, List, Union, SupportsIndex, Optional, Tuple)
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

class PlatformType(Enum):
    """平台类型枚举"""
    WINDOWS = auto()
    LINUX = auto()
    MACOS = auto()
    UNIX = auto()  # 其他UNIX系统
    JAVA = auto()  # Jython环境
    UNKNOWN = auto()

class PythonImplementation(Enum):
    """Python实现枚举"""
    CPYTHON = auto()
    PYPY = auto()
    IRONPYTHON = auto()
    JYTHON = auto()
    UNKNOWN = auto()

class ByteOrder(Enum):
    """字节序枚举"""
    LITTLE_ENDIAN = auto()
    BIG_ENDIAN = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class SystemInfo:
    """系统信息数据类"""
    system: str
    release: str
    version: str
    machine: str
    processor: str
    platform_type: PlatformType
    byte_order: ByteOrder

@dataclass(frozen=True)
class PythonBuildInfo:
    """Python构建信息数据类"""
    version: str
    version_tuple: Tuple[int, int, int]
    build_number: str
    build_date: str
    compiler: str
    build_options: Dict[str, bool]
    is_debug: bool
    is_wide_unicode: bool
    git_info: Optional[Tuple[str, str]] = None  # (commit_hash, branch)

@dataclass(frozen=True)
class PythonRuntimeInfo:
    """Python运行时信息数据类"""
    executable: str
    path: str
    flags: Dict[str, Any]
    byte_order: ByteOrder
    max_unicode: int
    implementation: PythonImplementation
    dll_path: Optional[str] = None
    prefix: Optional[str] = None
    base_prefix: Optional[str] = None

@dataclass(frozen=True)
class EnvironmentInfo:
    """环境信息数据类"""
    system: SystemInfo
    python_build: PythonBuildInfo
    python_runtime: PythonRuntimeInfo
    environment_vars: Dict[str, str]
    python_paths: Dict[str, List[str]]
    installed_packages: Dict[str, str]

class EnvironmentInspector:
    """
    终极Python环境检测工具
    
    特性:
    - 全面的系统信息检测
    - 详细的Python构建和运行时信息
    - 线程安全设计
    - 类型安全接口
    - 跨平台支持
    - 智能缓存机制
    - 依赖包检测
    """
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()
        self._package_cache = None
        self._package_cache_time = 0
        
    def get_system_info(self, refresh: bool = False) -> SystemInfo:
        """
        获取系统信息
        
        参数:
            refresh: 是否强制刷新缓存
            
        返回:
            SystemInfo对象
        """
        with self._lock:
            if not refresh and 'system_info' in self._cache:
                return self._cache['system_info']
            
            uname = platform.uname()
            system = uname.system
            platform_type = self._determine_platform_type(system)
            
            info = SystemInfo(
                system=system,
                release=uname.release,
                version=uname.version,
                machine=uname.machine,
                processor=uname.processor,
                platform_type=platform_type,
                byte_order=self._get_byteorder_enum()
            )
            
            self._cache['system_info'] = info
            return info
    
    def get_python_build_info(self, refresh: bool = False) -> PythonBuildInfo:
        """
        获取Python构建信息
        
        参数:
            refresh: 是否强制刷新缓存
            
        返回:
            PythonBuildInfo对象
        """
        with self._lock:
            if not refresh and 'build_info' in self._cache:
                return self._cache['build_info']
            
            version_tuple = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
            version = f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"
            build_str = sys.version
            build_parts = re.search(r'\((.+?)\)', build_str)
            build_info = build_parts.group(1) if build_parts else "unknown"
            
            # 解析构建日期和编译器
            build_date, compiler = self._parse_build_info(build_info)
            
            info = PythonBuildInfo(
                version=version,
                version_tuple=version_tuple,
                build_number=self._get_build_number(),
                build_date=build_date,
                compiler=compiler,
                build_options=self._parse_build_options(),
                is_debug=self._is_debug_build(),
                is_wide_unicode=sys.maxunicode > 0xFFFF,
                git_info=self._get_git_info()
            )
            
            self._cache['build_info'] = info
            return info
    
    def get_python_runtime_info(self, refresh: bool = False) -> PythonRuntimeInfo:
        """
        获取Python运行时信息
        
        参数:
            refresh: 是否强制刷新缓存
            
        返回:
            PythonRuntimeInfo对象
        """
        with self._lock:
            if not refresh and 'runtime_info' in self._cache:
                return self._cache['runtime_info']
            
            impl = self._get_implementation()
            dll_path = self._get_python_dll_path() if impl == PythonImplementation.CPYTHON else None
            
            info = PythonRuntimeInfo(
                executable=sys.executable,
                path=os.path.dirname(sys.executable),
                flags=self._get_runtime_flags(),
                byte_order=self._get_byteorder_enum(),
                max_unicode=sys.maxunicode,
                implementation=impl,
                dll_path=dll_path,
                prefix=sys.prefix,
                base_prefix=getattr(sys, 'base_prefix', sys.prefix)
            )
            
            self._cache['runtime_info'] = info
            return info
    
    def get_installed_packages(self, refresh: bool = False) -> Dict[str, str]:
        """
        获取已安装的Python包列表
        
        参数:
            refresh: 是否强制刷新缓存
            
        返回:
            包名到版本的字典
        """
        with self._lock:
            current_time = time.time()
            if not refresh and self._package_cache and current_time - self._package_cache_time < 300:  # 5分钟缓存
                return self._package_cache.copy()
            
            try:
                # 使用pip list命令获取包列表
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                packages = json.loads(result.stdout)
                package_dict = {pkg['name']: pkg['version'] for pkg in packages}
                
                self._package_cache = package_dict
                self._package_cache_time = current_time
                return package_dict
            except Exception as e:
                warnings.warn(f"获取安装包列表失败: {str(e)}")
                return {}
    
    def get_environment_info(self) -> EnvironmentInfo:
        """
        获取完整环境信息
        
        返回:
            EnvironmentInfo对象
        """
        with self._lock:
            return EnvironmentInfo(
                system=self.get_system_info(),
                python_build=self.get_python_build_info(),
                python_runtime=self.get_python_runtime_info(),
                environment_vars=self._get_environment_vars(),
                python_paths=self._get_python_paths(),
                installed_packages=self.get_installed_packages()
            )
    
    def _get_byteorder_enum(self) -> ByteOrder:
        """获取字节顺序枚举"""
        byteorder = sys.byteorder
        if byteorder == 'little':
            return ByteOrder.LITTLE_ENDIAN
        elif byteorder == 'big':
            return ByteOrder.BIG_ENDIAN
        else:
            return ByteOrder.UNKNOWN
    
    def _determine_platform_type(self, system: str) -> PlatformType:
        """确定平台类型"""
        system_lower = system.lower()
        if 'linux' in system_lower:
            return PlatformType.LINUX
        elif 'windows' in system_lower:
            return PlatformType.WINDOWS
        elif 'darwin' in system_lower or 'macos' in system_lower:
            return PlatformType.MACOS
        elif 'java' in system_lower:
            return PlatformType.JAVA
        elif any(unix in system_lower for unix in ['bsd', 'solaris', 'aix']):
            return PlatformType.UNIX
        else:
            return PlatformType.UNKNOWN
    
    def _get_build_number(self) -> str:
        """获取构建号"""
        if hasattr(sys, 'version_info') and hasattr(sys.version_info, 'build'):
            return str(sys.version_info.build[0])
        return "unknown"
    
    def _parse_build_info(self, build_str: str) -> Tuple[str, str]:
        """解析构建信息字符串"""
        # 尝试解析日期和编译器
        date_match = re.search(r'(\w{3} \d{1,2} \d{4},? \d{2}:\d{2}:\d{2})', build_str)
        date = date_match.group(0) if date_match else "unknown"
        
        compiler_match = re.search(r'\[(.*?)\]', build_str)
        compiler = compiler_match.group(1) if compiler_match else "unknown"
        
        return date, compiler
    
    def _parse_build_options(self) -> Dict[str, bool]:
        """解析构建选项"""
        build_str = sys.version
        options = {}
        
        # 常见构建选项检测
        common_options = [
            'WITH_PYMALLOC', 'WITH_THREAD', 'PYTHONFRAMEWORK',
            'WITH_DOC_STRINGS', 'WITH_VALGRIND', 'WITH_PYDEBUG'
        ]
        
        for opt in common_options:
            options[opt] = opt in build_str
        
        # 特殊选项检测
        options['PYMALLOC'] = 'pymalloc' in build_str.lower()
        options['DEBUG'] = 'debug' in build_str.lower()
        
        return options
    
    def _get_git_info(self) -> Optional[Tuple[str, str]]:
        """获取Git版本信息"""
        try:
            # 检查是否有git信息
            if not hasattr(sys, '_git'):
                return None
                
            git_info = sys._git
            return (git_info[0], git_info[1]) if git_info else None
        except Exception:
            return None
    
    def _is_debug_build(self) -> bool:
        """检查是否是调试版本"""
        return hasattr(sys, 'gettotalrefcount')
    
    def _get_implementation(self) -> PythonImplementation:
        """获取Python实现类型"""
        impl = sys.implementation.name.lower()
        if impl == 'cpython':
            return PythonImplementation.CPYTHON
        elif impl == 'pypy':
            return PythonImplementation.PYPY
        elif impl == 'ironpython':
            return PythonImplementation.IRONPYTHON
        elif impl == 'jython':
            return PythonImplementation.JYTHON
        else:
            return PythonImplementation.UNKNOWN
    
    def _get_runtime_flags(self) -> Dict[str, Any]:
        """获取运行时标志"""
        flags = sys.flags
        return {
            'debug': flags.debug,
            'inspect': flags.inspect,
            'interactive': flags.interactive,
            'optimize': flags.optimize,
            'dont_write_bytecode': flags.dont_write_bytecode,
            'no_user_site': flags.no_user_site,
            'no_site': flags.no_site,
            'ignore_environment': flags.ignore_environment,
            'verbose': flags.verbose,
            'bytes_warning': flags.bytes_warning,
            'quiet': flags.quiet,
            'hash_randomization': flags.hash_randomization,
            'isolated': flags.isolated,
            'dev_mode': flags.dev_mode,
            'utf8_mode': flags.utf8_mode,
            'warn_default_encoding': getattr(flags, 'warn_default_encoding', 0),
            'safe_path': getattr(flags, 'safe_path', False),
            'int_max_str_digits': getattr(flags, 'int_max_str_digits', 0)
        }
    
    def _get_python_dll_path(self) -> Optional[str]:
        """获取Python DLL路径"""
        if platform.system() != 'Windows':
            return None
            
        try:
            # Windows上获取Python DLL路径
            is_64bit = ctypes.sizeof(ctypes.c_void_p) == 8
            is_debug = hasattr(sys, 'gettotalrefcount')
            
            versions = [
                f"{sys.version_info.major}{sys.version_info.minor}",
                f"{sys.version_info.major}.{sys.version_info.minor}"
            ]
            
            suffixes = ['', '_d'] if is_debug else ['']
            
            for version in versions:
                for suffix in suffixes:
                    dll_name = f"python{version}{suffix}.dll"
                    try:
                        dll = ctypes.PyDLL(dll_name)
                        return os.path.abspath(dll._name)
                    except OSError:
                        continue
            
            return None
        except Exception:
            return None
    
    def _get_environment_vars(self) -> Dict[str, str]:
        """获取相关环境变量"""
        relevant_vars = [
            'PATH', 'PYTHONPATH', 'PYTHONHOME', 
            'VIRTUAL_ENV', 'CONDA_PREFIX',
            'LANG', 'LC_ALL', 'LC_CTYPE',
            'PYTHONSTARTUP', 'PYTHONDEBUG',
            'PYTHONINSPECT', 'PYTHONUNBUFFERED'
        ]
        return {var: os.getenv(var, '') for var in relevant_vars}
    
    def _get_python_paths(self) -> Dict[str, List[str]]:
        """获取Python路径信息"""
        return {
            'sys.path': sys.path,
            'module_search_paths': list(sys.path_importer_cache.keys()),
            'stdlib_paths': self._get_stdlib_paths()
        }
    
    def _get_stdlib_paths(self) -> List[str]:
        """获取标准库路径"""
        stdlib_paths = []
        for path in sys.path:
            if 'site-packages' not in path and 'dist-packages' not in path:
                stdlib_paths.append(path)
        return stdlib_paths

# 全局实例
_inspector = EnvironmentInspector()

# 便捷函数
def get_system_info() -> SystemInfo:
    """获取系统信息"""
    return _inspector.get_system_info()

def get_python_build_info() -> PythonBuildInfo:
    """获取Python构建信息"""
    return _inspector.get_python_build_info()

def get_python_runtime_info() -> PythonRuntimeInfo:
    """获取Python运行时信息"""
    return _inspector.get_python_runtime_info()

def get_installed_packages(refresh: bool = False) -> Dict[str, str]:
    """获取已安装的Python包列表"""
    return _inspector.get_installed_packages(refresh)

def get_environment_info() -> EnvironmentInfo:
    """获取完整环境信息"""
    return _inspector.get_environment_info()

def generate_environment_report(format: str = 'dict') -> Union[Dict[str, Any], str]:
    """
    生成环境报告
    
    参数:
        format: 输出格式 ('dict', 'json', 'yaml')
        
    返回:
        指定格式的报告
    """
    info = get_environment_info()
    
    def serialize(obj):
        if isinstance(obj, (SystemInfo, PythonBuildInfo, PythonRuntimeInfo, EnvironmentInfo)):
            return {k: serialize(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, tuple):
            return list(obj)
        return obj
    
    report_dict = serialize(info)
    
    if format == 'dict':
        return report_dict
    elif format == 'json':
        return json.dumps(report_dict, indent=2)
    elif format == 'yaml':
        import yaml
        return yaml.safe_dump(report_dict)
    else:
        raise ValueError(f"不支持的格式: {format}")