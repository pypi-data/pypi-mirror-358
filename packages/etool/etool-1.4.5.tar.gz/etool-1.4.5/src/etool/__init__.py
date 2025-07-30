"""
etool - 一个实用工具包
提供网络、办公、密码等各种实用功能的管理器
"""

import warnings
from typing import List, Dict, Tuple

# 存储成功导入的模块和失败信息
__all__: List[str] = []
_failed_imports: List[Tuple[str, str]] = []

# 网络模块
try:
    from ._network._speed import ManagerSpeed
    __all__.append("ManagerSpeed")
except ImportError as e:
    _failed_imports.append(("ManagerSpeed", str(e)))
    warnings.warn(f"Failed to import ManagerSpeed: {e}", ImportWarning)

try:
    from ._network._share import ManagerShare
    __all__.append("ManagerShare")
except ImportError as e:
    _failed_imports.append(("ManagerShare", str(e)))
    warnings.warn(f"Failed to import ManagerShare: {e}", ImportWarning)

# 其他工具模块
try:
    from ._other._password import ManagerPassword
    __all__.append("ManagerPassword")
except ImportError as e:
    _failed_imports.append(("ManagerPassword", str(e)))
    warnings.warn(f"Failed to import ManagerPassword: {e}", ImportWarning)

try:
    from ._other._scheduler import ManagerScheduler
    __all__.append("ManagerScheduler")
except ImportError as e:
    _failed_imports.append(("ManagerScheduler", str(e)))
    warnings.warn(f"Failed to import ManagerScheduler: {e}", ImportWarning)

try:
    from ._other._install import ManagerInstall
    __all__.append("ManagerInstall")
except ImportError as e:
    _failed_imports.append(("ManagerInstall", str(e)))
    warnings.warn(f"Failed to import ManagerInstall: {e}", ImportWarning)

try:
    from ._other._menu import ManagerMenu
    __all__.append("ManagerMenu")
except ImportError as e:
    _failed_imports.append(("ManagerMenu", str(e)))
    warnings.warn(f"Failed to import ManagerMenu: {e}", ImportWarning)

# 办公工具模块
try:
    from ._office._image import ManagerImage
    __all__.append("ManagerImage")
except ImportError as e:
    _failed_imports.append(("ManagerImage", str(e)))
    warnings.warn(f"Failed to import ManagerImage: {e}", ImportWarning)

try:
    from ._office._email import ManagerEmail
    __all__.append("ManagerEmail")
except ImportError as e:
    _failed_imports.append(("ManagerEmail", str(e)))
    warnings.warn(f"Failed to import ManagerEmail: {e}", ImportWarning)

try:
    from ._office._docx import ManagerDocx
    __all__.append("ManagerDocx")
except ImportError as e:
    _failed_imports.append(("ManagerDocx", str(e)))
    warnings.warn(f"Failed to import ManagerDocx: {e}", ImportWarning)

try:
    from ._office._excel import ManagerExcel
    __all__.append("ManagerExcel")
except ImportError as e:
    _failed_imports.append(("ManagerExcel", str(e)))
    warnings.warn(f"Failed to import ManagerExcel: {e}", ImportWarning)

try:
    from ._office._ipynb import ManagerIpynb
    __all__.append("ManagerIpynb")
except ImportError as e:
    _failed_imports.append(("ManagerIpynb", str(e)))
    warnings.warn(f"Failed to import ManagerIpynb: {e}", ImportWarning)

try:
    from ._office._qrcode import ManagerQrcode
    __all__.append("ManagerQrcode")
except ImportError as e:
    _failed_imports.append(("ManagerQrcode", str(e)))
    warnings.warn(f"Failed to import ManagerQrcode: {e}", ImportWarning)

try:
    from ._office._pdf import ManagerPdf
    __all__.append("ManagerPdf")
except ImportError as e:
    _failed_imports.append(("ManagerPdf", str(e)))
    warnings.warn(f"Failed to import ManagerPdf: {e}", ImportWarning)

# Markdown 模块
try:
    from ._md._md_to_docx import ManagerMd
    __all__.append("ManagerMd")
except ImportError as e:
    _failed_imports.append(("ManagerMd", str(e)))
    warnings.warn(f"Failed to import ManagerMd: {e}", ImportWarning)


def get_import_status() -> Dict[str, List]:
    """
    获取模块导入状态
    
    Returns:
        dict: 包含 'available' 和 'failed' 键的字典
    """
    return {
        "available": __all__.copy(),
        "failed": _failed_imports.copy(),
    }


def is_available(module_name: str) -> bool:
    """
    检查指定模块是否可用
    
    Args:
        module_name: 模块名称
        
    Returns:
        bool: 模块是否可用
    """
    return module_name in __all__


def get_version() -> str:
    """获取版本信息"""
    return "1.0.0"
