from types import UnionType
from typing import *

type AnyType = Type | TypeAliasType | NewType | UnionType
type AnyTypeOrTypes = AnyType | Iterable[AnyTypeOrTypes]

def str_join(items: Iterable[str], *, conjunction: str = 'or') -> str:
    """ Joins a sequence of strings with commas and a conjunction. """
    match tuple(items):
        case ():
            return ""
        case (el, ):
            return el
        case (el1, el2):
            return f"{el1} {conjunction} {el2}"
        case (*els, last):
            return ', '.join(els) + f", {conjunction} {last}"
        case _:
            raise TypeError(f"Cannot join {items!r}")

def type_flatten(t: AnyTypeOrTypes) -> Iterable[str]:
    """ Flattens a type or sequence of types into a sequence of type names. """
    match (t):
        case NewType():
            yield t.__name__
        case TypeAliasType():
            yield t.__name__
        case UnionType():
            yield from (type_flatten(t.__args__))
        case type():
            yield t.__name__
        case it if isinstance(it, Iterable):
            for typ in it:
                yield from type_flatten(typ)

def type_repr(t: AnyTypeOrTypes) -> str:
    """ Returns a string representation of a type or sequence of types. """
    return str_join(type_flatten(t), conjunction='or')


__all__ = \
[
    'AnyType',
    'AnyTypeOrTypes',
    
    'type_repr',
    'type_flatten',
    'str_join',
]
