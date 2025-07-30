from abc import ABC, abstractmethod
from typing import *

from dataclassabc import dataclassabc

from .types import type_repr, AnyTypeOrTypes


@dataclass_transform(frozen_default=True)
def dataclass_exception(cls = None, /, **kwargs):
    """ A dataclass decorator which should be used on all subclasses of `BaseExceptionABC`. """
    kwargs['frozen'] = True
    if (cls is not None):
        return dataclassabc(**kwargs)(cls)
    else:
        return dataclassabc(**kwargs)


@dataclass_exception
class BaseExceptionABC(Exception, ABC):
    """ Base class for any exceptions within the package. """
    def __post_init__(self):
        super().__init__(self.message)
    
    @property
    @abstractmethod
    def message(self) -> str:
        pass
    
    def __init_subclass__(cls, **kwargs):
        # assert cls.__name__ != 'GenericException'
        pass

@final
@dataclass_exception
class GenericException(BaseExceptionABC):
    """
    A generic exception class with only one parameter: `message`.
    Analogue of `builtin.Exception`.
    Marked as `@final` to prevent abusing.
    """
    
    message: str

@dataclass_exception
class InvalidArgumentTypeError(BaseExceptionABC, TypeError):
    """ A `TypeError` subclass with a more detailed message when calling with wrong argument types. """
    
    name: str
    expected: AnyTypeOrTypes
    actual: Any
    
    @property
    def message(self):
        return f"Invalid argument {self.name!r} type: Expected {type_repr(self.expected)}, got {type(self.actual)} instead."


@dataclass_exception
class InvalidSignature(BaseExceptionABC, TypeError):
    """ A `TypeError` subclass with a more detailed message when calling an overloaded function with unknown call signature. """
    name: str
    
    @property
    def message(self):
        return f"Invalid {self.name} signature."


__all__ = \
[
    'BaseExceptionABC',
    'GenericException',
    'InvalidArgumentTypeError',
    'InvalidSignature',
    
    'dataclass_exception',
]
