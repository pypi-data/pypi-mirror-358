# Dataclass Exceptions

**DISCLAIMER:** This package requires Python 3.12+ and is unlikely to be backported.

Are you tired of exception instances which can't hold any metadata?
Then this is the Python package for you!
It declares interfaces for exceptions to use within your code base those ARE dataclasses!
With nice constructors, field access,
and a special `message` property which contains human-readable text!
Isn't it beautiful?

**Before:**
```python
def func(arg: str | int | None):
    if (arg is None):
        print("arg is None")
    elif (isinstance(arg, str)):
        print("arg is str")
    elif (isinstance(arg, int)):
        print("arg is int")
    else:
        raise TypeError(f"Argument 'arg' has wrong type, expected str, int, or None, got {type(arg)}")
```

**After:**
```python
from dataclass_exceptions.errors import InvalidArgumentTypeError

def func(arg: str | int | None):
    match (arg):
        case None:
            print("arg is None")
        case str():
            print("arg is str")
        case int():
            print("arg is int")
        case _:
            # Non-keyword call is also OK:
            # raise InvalidArgumentTypeError('arg', str|int|None, arg)
            raise InvalidArgumentTypeError(name='arg', expected=str | int | None, actual=arg)
```

Error message is generated automatically:
```text
dataclass_exceptions.errors.InvalidArgumentTypeError: Invalid argument 'arg' type: Expected str, int, or NoneType, got <class 'float'> instead.
```

And you may access exception fields at any time!
```python
try:
    func(5.6)
except InvalidArgumentTypeError as exc:
    print(f"Caught argument exception: {exc.message} (value: {exc.actual})")
```
```text
Caught argument exception: Invalid argument 'arg' type: Expected str, int, or NoneType, got <class 'float'> instead. (value: 5.6)
```

## Usage
This module declares the base exception class `dataclass_exceptions.errors.BaseExceptionABC` which cannot be instantiated directly,
but which declares interface for all exceptions within the module.
You may and should derive your exceptions from this one.

```python
from dataclass_exceptions import BaseExceptionABC, dataclass_exception
from dataclasses import dataclass

@dataclass_exception # Sets required dataclass flags
class CustomException(BaseExceptionABC):
    @property
    def message(self) -> str:
        """ The magic is done here """
        return "Custom exception detailed text"

@dataclass_exception
class ParameterizedException(BaseExceptionABC):
    param_one = "Parameters are ok, too"
    
    @property
    def message(self) -> str:
        """ The magic is done here """
        return f"Parameterized exception with argument param_one={self.param_one!r}"

# You can declare your abstract exception base, too!
from abc import ABC
@dataclass_exception
class LibraryBaseException(BaseExceptionABC, ABC):
    pass

# You can inherit any exception subclass, even Warnings!
@dataclass_exception
class LibraryWarning(LibraryBaseException, UserWarning):
    @property
    def message(self) -> str:
        return "This is custom warning"

@dataclass_exception
class LibraryGenericException(LibraryBaseException):
    message: str  # Sometimes, you only need a customizable message
```

### Members
#### Module `dataclass_exceptions.errors`
A module implementing exception classes:
 * `dataclass_exception`, also available as `dataclass_exceptions.BaseExceptionABC`:
   A function wrapping the given `BaseExceptionABC` child to be a valid exception dataclass.
 * `BaseExceptionABC`, also available as `dataclass_exceptions.BaseExceptionABC`:
   Base class for all exceptions within the package.
 * `GenericException`:
   A generic exception class with only one parameter: `message`.
   Analogue of `builtin.Exception`.
   Marked as `@final` to prevent abusing.
 * `InvalidArgumentTypeError`:
   A `TypeError` subclass with a more detailed message when calling with wrong argument types.
 * `InvalidSignature`:
   A `TypeError` subclass with a more detailed message when calling
   an overloaded function with unknown call signature.

#### Module `dataclass_exceptions.types`
A module with helper functions for casting types to strings:
 * `str_join(items: Iterable[str], *, conjunction: str = 'or') -> str`:
    Joins a sequence of strings with commas and a conjunction on the end.
 * `type_repr(t: Type | Iterable[Type]) -> str`:
    Returns a string representation of a type or sequence of types.
 * `type_flatten(t: Type | Iterable[Type]) -> Iterable[str]`:
    Flattens a type or sequence of types into a sequence of type names.


## Licensing
*see: [LICENSE.txt](./LICENSE.txt)*

[BSD-2 License].
Copyright (c) Peter Zaitcev, 2025.

<!-- Links -->
[BSD-2 License]: https://opensource.org/license/bsd-2-clause
