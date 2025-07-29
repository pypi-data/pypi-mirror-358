"""
### PyPlugin - Python 高级插件库
##### 概述
PyPlugin 是一个功能强大的 Python 插件系统框架，提供了完整的插件开发、加载和执行解决方案。该系统特别适合构建可扩展的应用程序，支持：

- 插件生命周期管理：自动处理插件的加载、验证和执行
- 智能依赖检查：支持版本规范的依赖管理 (package>=1.2.0)
- 元数据验证：自动检查插件元数据的完整性和合理性
- 优先级系统：数值越小优先级越高(1-100范围)
- 彩色终端输出：使用 Rich 库提供直观的状态反馈
- 插件隔离：可选在独立进程中运行插件
- 热重载支持：动态重新加载插件而不重启应用
- 配置系统：支持插件级别的配置管理
"""

import importlib
import os
import sys
import inspect
from collections import OrderedDict
from pathlib import Path
from multiprocessing import Process, Queue
from typing import Type, List, Dict, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum, auto

from rich import print as rich_print
from rich.table import Table
from rich.panel import Panel
from packaging.version import parse as parse_version
import yaml


class PluginState(Enum):
    """插件状态枚举"""
    UNLOADED = auto()
    LOADED = auto()
    INITIALIZED = auto()
    READY = auto()
    ERROR = auto()


@dataclass
class PluginConfig:
    """插件配置数据类"""
    enabled: bool = True
    priority: Optional[int] = None
    config: Dict[str, Any] = field(default_factory=dict)


class PluginBase(ABC):
    """插件基类，支持高级扩展功能"""
    
    # 类属性定义元数据（子类可覆盖）
    metadata = {
        "name": "Unnamed Plugin",
        "version": "1.0.0",
        "author": "Anonymous",
        "description": "No description provided",
        "category": "uncategorized"
    }
    
    # 定义插件依赖包（子类可覆盖）
    required_packages: List[str] = []
    
    # 默认执行优先级（数值越小优先级越高）
    priority: int = 50
    
    # 是否在独立进程中运行
    run_in_process: bool = False
    
    # 插件状态
    _state: PluginState = PluginState.UNLOADED
    
    def __init__(self):
        """初始化时自动检查依赖和元数据"""
        self._check_metadata()
        self._check_dependencies()
        self._state = PluginState.INITIALIZED
        self._config = PluginConfig()
        
    def _check_dependencies(self):
        """验证依赖包是否已安装，并检查版本要求"""
        missing = []
        invalid = []
        version_issues = []
        
        for dep in self.required_packages:
            try:
                # 处理版本规范
                if any(op in dep for op in [">", "<", "=", "!"]):
                    pkg_name = dep.split('>')[0].split('<')[0].split('=')[0].split('!')[0].strip()
                    version_spec = dep[len(pkg_name):].strip()
                else:
                    pkg_name = dep
                    version_spec = None
                
                # 尝试导入模块
                module = importlib.import_module(pkg_name)
                
                # 检查版本要求
                if version_spec and hasattr(module, "__version__"):
                    installed_version = module.__version__
                    if not self._check_version_constraint(installed_version, version_spec):
                        version_issues.append(
                            f"{pkg_name} (需要 {version_spec}, 当前 {installed_version})"
                        )
                        
            except ModuleNotFoundError:
                missing.append(pkg_name)
            except ImportError:
                invalid.append(f"{pkg_name} (导入失败)")
            except Exception as e:
                invalid.append(f"{pkg_name} ({str(e)})")
        
        # 如果有错误则抛出异常
        if missing or invalid or version_issues:
            error_msg = []
            if missing:
                error_msg.append(
                    f"缺少依赖: {', '.join(missing)}\n"
                    f"请安装: pip install {' '.join(missing)}"
                )
            if invalid:
                error_msg.append(f"无效依赖: {', '.join(invalid)}")
            if version_issues:
                error_msg.append(f"版本冲突: {', '.join(version_issues)}")
            
            self._state = PluginState.ERROR
            raise ImportError("\n".join(error_msg))
    
    def _check_version_constraint(self, version: str, constraint: str) -> bool:
        """检查版本是否符合约束条件"""
        current = parse_version(version)
        
        if ">=" in constraint:
            required = parse_version(constraint.split(">=")[1])
            return current >= required
        elif "<=" in constraint:
            required = parse_version(constraint.split("<=")[1])
            return current <= required
        elif "==" in constraint:
            required = parse_version(constraint.split("==")[1])
            return current == required
        elif "!=" in constraint:
            required = parse_version(constraint.split("!=")[1])
            return current != required
        elif ">" in constraint:
            required = parse_version(constraint.split(">")[1])
            return current > required
        elif "<" in constraint:
            required = parse_version(constraint.split("<")[1])
            return current < required
        else:
            return True
    
    def _check_metadata(self):
        """检查元数据是否被正确覆盖"""
        default_meta = PluginBase.metadata
        current_meta = self.metadata
        
        # 检查所有默认元数据字段是否存在
        missing_fields = [field for field in default_meta if field not in current_meta]
        
        # 检查是否有字段使用默认值
        default_values = [field for field in default_meta if current_meta.get(field) == default_meta[field]]
        
        if missing_fields:
            rich_print(f"[yellow]⚠️ 元数据字段缺失: {', '.join(missing_fields)}[/yellow]")
        
        if default_values:
            rich_print(f"[yellow]⚠️ 使用默认元数据值: {', '.join(default_values)}[/yellow]")
        
        # 检查关键字段是否有效
        if current_meta.get("name") == "Unnamed Plugin":
            rich_print("[yellow]⚠️ 插件名称未定义，使用默认名称[/yellow]")
        
        if current_meta.get("version") == "1.0.0":
            rich_print("[yellow]⚠️ 插件版本未定义，使用默认版本[/yellow]")

    def get_plugin_name(self) -> str:
        """获取插件名称"""
        return self.metadata['name']
    
    def get_state(self) -> PluginState:
        """获取当前插件状态"""
        return self._state
    
    def configure(self, config: Dict[str, Any]):
        """配置插件"""
        self._config.config.update(config)
    
    def initialize(self):
        """初始化插件资源"""
        self._state = PluginState.READY
    
    def cleanup(self):
        """清理插件资源"""
        self._state = PluginState.INITIALIZED
    
    @abstractmethod
    def execute(self, data: Any) -> Any:
        """插件核心处理方法"""
        self._state = PluginState.READY
        pass

    @classmethod
    def get_metadata(cls) -> Dict[str, str]:
        """获取插件元数据"""
        return cls.metadata.copy()


class PluginManager:
    """插件管理器，负责插件的加载、管理和执行"""
    
    def __init__(self):
        self._plugins: List[PluginBase] = []
        self._plugin_configs: Dict[str, PluginConfig] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._config_file = "plugins_config.yaml"
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载插件配置"""
        if os.path.exists(self._config_file):
            with open(self._config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
                for plugin_name, config in config_data.items():
                    self._plugin_configs[plugin_name] = PluginConfig(**config)
    
    def _save_config(self):
        """保存插件配置到文件"""
        config_data = {}
        for name, config in self._plugin_configs.items():
            config_data[name] = {
                "enabled": config.enabled,
                "priority": config.priority,
                "config": config.config
            }
        
        with open(self._config_file, 'w') as f:
            yaml.safe_dump(config_data, f)
    
    def discover_plugins(self, directory: str = "plugins") -> List[str]:
        """发现指定目录下的所有插件"""
        plugin_dir = Path(directory)
        if not plugin_dir.exists():
            return []
        
        plugin_files = []
        for file in plugin_dir.glob("**/*.py"):
            if file.name.startswith("_"):
                continue
            plugin_files.append(str(file))
        
        return plugin_files
    
    def load_plugin_from_file(self, filepath: str) -> bool:
        """从文件加载插件"""
        try:
            # 动态加载模块
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None:
                raise ImportError(f"无效的Python模块: {filepath}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找所有合法插件类
            loaded = False
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginBase) and 
                    obj != PluginBase and 
                    obj.__module__ == module.__name__):
                    
                    self._plugin_classes[name] = obj
                    if name not in self._plugin_configs:
                        self._plugin_configs[name] = PluginConfig()
                    loaded = True
            
            return loaded
        
        except Exception as e:
            rich_print(f"[red]加载插件 {filepath} 失败: {str(e)}[/red]")
            return False
    
    def load_all_plugins(self, directory: str = "plugins") -> int:
        """加载目录下的所有插件"""
        plugin_files = self.discover_plugins(directory)
        count = 0
        for file in plugin_files:
            if self.load_plugin_from_file(file):
                count += 1
        
        rich_print(f"[green]成功加载 {count}/{len(plugin_files)} 个插件[/green]")
        return count
    
    def instantiate_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """实例化指定插件"""
        if plugin_name not in self._plugin_classes:
            return None
        
        plugin_class = self._plugin_classes[plugin_name]
        config = self._plugin_configs.get(plugin_name, PluginConfig())
        
        try:
            instance = plugin_class()
            
            # 应用配置
            if config.priority is not None:
                instance.priority = config.priority
            if config.config:
                instance.configure(config.config)
            
            # 初始化插件
            instance.initialize()
            
            # 插入到插件列表并保持排序
            self._insert_plugin_sorted(instance)
            
            return instance
        except Exception as e:
            rich_print(f"[red]实例化插件 {plugin_name} 失败: {str(e)}[/red]")
            return None
    
    def _insert_plugin_sorted(self, plugin: PluginBase):
        """按优先级将插件插入到正确位置"""
        for i, p in enumerate(self._plugins):
            if p.priority > plugin.priority:
                self._plugins.insert(i, plugin)
                return
        self._plugins.append(plugin)
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取已加载的插件实例"""
        for plugin in self._plugins:
            if plugin.get_plugin_name() == plugin_name:
                return plugin
        return None
    
    def get_all_plugins(self) -> List[PluginBase]:
        """获取所有已加载插件"""
        return self._plugins.copy()
    
    def execute_plugin(self, plugin_name: str, data: Any) -> Any:
        """执行指定插件"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"插件 {plugin_name} 未加载")
        
        if plugin.run_in_process:
            return self._execute_in_process(plugin, data)
        else:
            return plugin.execute(data)
    
    def _execute_in_process(self, plugin: PluginBase, data: Any) -> Any:
        """在独立进程中执行插件"""
        def _worker(plugin_class: Type[PluginBase], data: Any, queue: Queue):
            try:
                instance = plugin_class()
                instance.initialize()
                result = instance.execute(data)
                queue.put(("success", result))
            except Exception as e:
                queue.put(("error", str(e)))
        
        q = Queue()
        p = Process(target=_worker, args=(plugin.__class__, data, q))
        p.start()
        p.join()
        
        status, result = q.get()
        if status == "error":
            raise RuntimeError(f"插件执行失败: {result}")
        return result
    
    def execute_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """按优先级顺序执行所有插件，支持插件特定的输入数据
        
        参数:
            data: 字典格式，键为插件名称，值为该插件的输入数据
            
        返回:
            字典格式的执行结果，键为插件名称，值为执行结果或错误信息
            
        示例:
            >>> data = {
            ...     "Plugin1": {"param1": "value1"},
            ...     "Plugin2": [1, 2, 3]
            ... }
            >>> manager.execute_pipeline(data)
            {
                "Plugin1": {"result": "success"},
                "Plugin2": {"error": "Invalid input"}
            }
        """
        results = {}
        for plugin in self._plugins:
            plugin_name = plugin.get_plugin_name()
            
            # 检查插件是否启用
            if not self._plugin_configs.get(plugin_name, PluginConfig()).enabled:
                continue
                
            try:
                # 获取该插件的输入数据，如果没有则为None
                plugin_data = data.get(plugin_name)
                
                # 执行插件
                results[plugin_name] = self.execute_plugin(plugin_name, plugin_data)
                
            except Exception as e:
                rich_print(f"[red]插件 {plugin_name} 执行失败: {str(e)}[/red]")
                results[plugin_name] = {
                    "error": str(e),
                    "type": type(e).__name__,
                    "plugin": plugin_name
                }
        
        return results

    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        if plugin_name not in self._plugin_classes:
            return False
        
        # 移除现有实例
        self._plugins = [p for p in self._plugins if p.get_plugin_name() != plugin_name]
        
        # 重新实例化
        return self.instantiate_plugin(plugin_name) is not None
    
    def show_plugin_info(self):
        """显示所有插件信息"""
        table = Table(title="已加载插件", show_header=True, header_style="bold magenta")
        table.add_column("名称", style="cyan")
        table.add_column("版本", style="green")
        table.add_column("作者")
        table.add_column("描述")
        table.add_column("优先级")
        table.add_column("状态")
        
        for plugin in self._plugins:
            meta = plugin.metadata
            table.add_row(
                meta["name"],
                meta["version"],
                meta["author"],
                meta["description"],
                str(plugin.priority),
                plugin.get_state().name
            )
        
        rich_print(table)
    
    def set_plugin_priority(self, plugin_name: str, priority: int):
        """设置插件优先级并重新排序"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"插件 {plugin_name} 未找到")
        
        plugin.priority = priority
        self._plugins.remove(plugin)
        self._insert_plugin_sorted(plugin)
        
        # 更新配置
        if plugin_name in self._plugin_configs:
            self._plugin_configs[plugin_name].priority = priority
            self._save_config()
    
    def enable_plugin(self, plugin_name: str, enable: bool = True):
        """启用或禁用插件"""
        if plugin_name in self._plugin_configs:
            self._plugin_configs[plugin_name].enabled = enable
            self._save_config()
    
    def get_plugin_config(self, plugin_name: str) -> Optional[PluginConfig]:
        """获取插件配置"""
        return self._plugin_configs.get(plugin_name)
    
    def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """更新插件配置"""
        if plugin_name in self._plugin_configs:
            self._plugin_configs[plugin_name].config.update(config)
            self._save_config()
            
            # 如果插件已加载，则应用新配置
            plugin = self.get_plugin(plugin_name)
            if plugin:
                plugin.configure(config)


# 全局插件管理器实例
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器实例"""
    return _plugin_manager


def load_plugins_from_directory(directory: str = "plugins") -> int:
    """从目录加载所有插件"""
    return _plugin_manager.load_all_plugins(directory)


def execute_pipeline(data: Any) -> Dict[str, Any]:
    """执行插件管道"""
    return _plugin_manager.execute_pipeline(data)


def show_plugin_info():
    """显示插件信息"""
    _plugin_manager.show_plugin_info()


def reload_plugin(plugin_name: str) -> bool:
    """重新加载插件"""
    return _plugin_manager.reload_plugin(plugin_name)


def set_plugin_priority(plugin_name: str, priority: int):
    """设置插件优先级"""
    _plugin_manager.set_plugin_priority(plugin_name, priority)


def enable_plugin(plugin_name: str, enable: bool = True):
    """启用或禁用插件"""
    _plugin_manager.enable_plugin(plugin_name, enable)


def get_plugin(plugin_name: str) -> Optional[PluginBase]:
    """获取插件实例"""
    return _plugin_manager.get_plugin(plugin_name)


def execute_plugin(plugin_name: str, data: Any) -> Any:
    """执行单个插件"""
    return _plugin_manager.execute_plugin(plugin_name, data)


def update_plugin_config(plugin_name: str, config: Dict[str, Any]):
    """更新插件配置"""
    _plugin_manager.update_plugin_config(plugin_name, config)