# -*-coding:utf-8-*-
"""
JIT Utils Backend - 极态后端工具包

A comprehensive utility package for backend development with JIT.

主要功能:
- 时间处理工具
- 字符串处理工具
- 二维码和条形码生成
- 数据验证
- 网络工具
- 签名工具
等等...
"""

__version__ = '0.0.1'
__author__ = 'zangtao'

# 导入主要的工具类和函数
try:
    from .decorator import forward
except ImportError:
    pass

# 时间工具
try:
    from . import time as time_utils
    # 导出一些常用的时间函数
    from .time import (
        now, today, get, dayShift,
        monday, weekShift, monthStart, monthShift,
        quarterStart, quarterShift, yearStart, yearShift,
        getTimestamp, timeStampToDateTime, strToTimestamp,
        formatNow, datetime2string, string2datetime
    )
except ImportError:
    pass

# 字符串工具
try:
    from . import string as string_utils
    from .string import (
        randomString, randomNum, getUuidStr,
        md5Bytes, md5Str, getFileMd5,
        renderTemplateString
    )
except ImportError:
    pass

# 二维码工具
try:
    from .qrcode import Qrcode
except ImportError:
    Qrcode = None

# 条形码工具
try:
    from .barcode import Barcode
except ImportError:
    Barcode = None

# 验证工具
try:
    from .validator import ParamsValidator
except ImportError:
    ParamsValidator = None

# 网络工具
try:
    from . import network
except ImportError:
    pass

# 签名工具
try:
    from . import signature
except ImportError:
    pass

# 匹配工具
try:
    from . import matchTool
except ImportError:
    pass

# 类工具
try:
    from . import clsTool
except ImportError:
    pass

# 转换工具
try:
    from .convert import Converter, MemoryCompiler
except ImportError:
    # 如果导入失败，创建占位符避免 __all__ 报错
    Converter = None
    MemoryCompiler = None

# 异常处理
try:
    from . import exceptions
except ImportError:
    pass

# 工作日常量
try:
    from . import workday_constants
except ImportError:
    pass

# 配置相关
try:
    from . import config
except ImportError:
    pass

# 定义 __all__ 列表，控制 from jit_utils import * 的行为
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    
    # 装饰器
    'forward',
    
    # 时间工具
    'time_utils',
    'now', 'today', 'get', 'dayShift',
    'monday', 'weekShift', 'monthStart', 'monthShift',
    'quarterStart', 'quarterShift', 'yearStart', 'yearShift',
    'getTimestamp', 'timeStampToDateTime', 'strToTimestamp',
    'formatNow', 'datetime2string', 'string2datetime',
    
    # 字符串工具
    'string_utils',
    'randomString', 'randomNum', 'getUuidStr',
    'md5Bytes', 'md5Str', 'getFileMd5',
    'renderTemplateString',
    
    # 二维码和条形码
    'Qrcode', 'Barcode',
    
    # 验证工具
    'ParamsValidator',
    
    # 其他模块
    'network', 'signature', 'matchTool',
    'clsTool', 'exceptions', 'workday_constants',
    'config', 'Converter', 'MemoryCompiler'
]
