"""
.. include:: ../../README.md
"""

from collections import namedtuple

__title__ = 'dataclass-exceptions'
__author__ = 'Peter Zaitcev / USSX-Hares'
__license__ = 'BSD 2-clause license'
__copyright__ = 'Copyright 2025 Peter Zaitcev'
__version__ = '0.1.1'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(*__version__.split('.'), releaselevel='alpha', serial=0)

__all__ = \
[
    'version_info',
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
    '__version__',
    
    'BaseExceptionABC',
    'dataclass_exception',
]

from .errors import BaseExceptionABC, dataclass_exception
