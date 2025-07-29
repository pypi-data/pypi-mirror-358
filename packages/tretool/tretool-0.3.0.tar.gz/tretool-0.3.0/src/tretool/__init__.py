"""
# tretool

## tretool - Python多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**tretool** 是一个集成常用功能的Python工具库。
"""

import sys

MIN_PY_VERSION = (3, 10)

if sys.version_info >= MIN_PY_VERSION:
    from . import config

    from . import decoratorlib

    from . import encoding

    from . import httplib

    from . import jsonlib

    from . import logger

    from . import path
    from . import platformlib
    from . import plugin

    from . import smartCache

    from . import timelib
    from . import transform

else:
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    required_version = f"{MIN_PY_VERSION[0]}.{MIN_PY_VERSION[1]}"

    raise RuntimeError(
            f"\n\n"
            f"不兼容的Python版本\n\n"
            f"Tretool需要Python {required_version}+ (检测到: Python {current_version})\n"
            f"请执行以下操作之一:\n"
            f"1. 升级Python到{required_version}或更高版本\n"
            f"2. 使用兼容的Tretool版本\n\n"
            f"升级Python推荐方法:\n"
            f"- 使用pyenv: `pyenv install 3.10.x`\n"
            f"- 从官网下载: https://www.python.org/downloads/\n"
            f"- 使用conda: `conda install python=3.10`"
        )