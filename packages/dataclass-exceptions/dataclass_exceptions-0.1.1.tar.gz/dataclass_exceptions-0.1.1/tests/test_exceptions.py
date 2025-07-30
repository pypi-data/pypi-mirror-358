import contextlib
import warnings
from dataclasses import dataclass
from typing import *
from unittest import TestCase

from dataclassabc import dataclassabc

from dataclass_exceptions.errors import *


class ExceptionsTestCase(TestCase):
    def test_can_raise(self):
        with self.subTest("Generic"):
            with self.assertRaises(GenericException) as cm:
                raise GenericException("generic message")
            self.assertEqual(cm.exception.message, "generic message")
        
        with self.subTest("InvalidArgumentTypeError"):
            with self.assertRaises(InvalidArgumentTypeError) as cm:
                raise InvalidArgumentTypeError("argument name", str, 101)
            
            self.assertEqual(cm.exception.name, "argument name")
            self.assertEqual(cm.exception.expected, str)
            self.assertEqual(cm.exception.actual, 101)
            self.assertEqual(cm.exception.message, "Invalid argument 'argument name' type: Expected str, got <class 'int'> instead.")
        
        with self.subTest("InvalidSignature"):
            with self.assertRaises(InvalidSignature) as cm:
                raise InvalidSignature("function_name")
            
            self.assertEqual(cm.exception.name, "function_name")
            self.assertEqual(cm.exception.message, "Invalid function_name signature.")
    
    def test_can_reraise(self):
        with self.subTest("Generic"):
            with self.assertRaises(GenericException) as cm:
                try:
                    raise GenericException("generic message")
                except Exception:
                    raise
            
            self.assertEqual(cm.exception.message, "generic message")
        
        with self.subTest("InvalidArgumentTypeError"):
            with self.assertRaises(InvalidArgumentTypeError) as cm:
                try:
                    raise InvalidArgumentTypeError("argument name", str, 101)
                except Exception:
                    raise
            
            self.assertEqual(cm.exception.message, "Invalid argument 'argument name' type: Expected str, got <class 'int'> instead.")
        
        with self.subTest("InvalidSignature"):
            with self.assertRaises(InvalidSignature) as cm:
                try:
                    raise InvalidSignature("function_name")
                except Exception:
                    raise
            
            self.assertEqual(cm.exception.message, "Invalid function_name signature.")
    
    def test_can_raise_from(self):
        with self.subTest("Generic"):
            with self.assertRaises(GenericException) as cm:
                try:
                    raise Exception(...)
                except Exception as e:
                    raise GenericException("generic message") from e
            
            self.assertEqual(cm.exception.message, "generic message")
        
        with self.subTest("InvalidArgumentTypeError"):
            with self.assertRaises(InvalidArgumentTypeError) as cm:
                try:
                    raise Exception(...)
                except Exception as e:
                    raise InvalidArgumentTypeError("argument name", str, 101) from e
            
            self.assertEqual(cm.exception.message, "Invalid argument 'argument name' type: Expected str, got <class 'int'> instead.")
        
        with self.subTest("InvalidSignature"):
            with self.assertRaises(InvalidSignature) as cm:
                try:
                    raise Exception(...)
                except Exception as e:
                    raise InvalidSignature("function_name") from e
            
            self.assertEqual(cm.exception.message, "Invalid function_name signature.")
    
    def test_can_be_derived(self):
        with self.subTest("Generic"):
            with self.assertRaises(ImportError) as cm:
                try:
                    raise GenericException("generic message")
                except Exception as e:
                    raise ImportError from e
        
        with self.subTest("InvalidArgumentTypeError"):
            with self.assertRaises(ImportError) as cm:
                try:
                    raise InvalidArgumentTypeError("argument name", str, 101)
                except Exception as e:
                    raise ImportError from e
        
        with self.subTest("InvalidSignature"):
            with self.assertRaises(ImportError) as cm:
                try:
                    raise InvalidSignature("function_name")
                except Exception as e:
                    raise ImportError from e
    
    def test_works_in_context_mgr(self):
        exc_gens: List[Callable[[], BaseExceptionABC]] = \
        [
            lambda: GenericException("generic message"),
            lambda: InvalidArgumentTypeError("argument name", str, 101),
            lambda: InvalidSignature("function_name"),
        ]
        
        for exc_gen in exc_gens:
            exc_example = exc_gen()
            exc_type = type(exc_example)
            
            with self.subTest("Context manager re-raises:", exc_type=exc_type.__name__):
                @contextlib.contextmanager
                def context_manager_reraises():
                    try:
                        yield
                    except Exception:
                        raise
                
                with self.assertRaises(exc_type) as cm:
                    with context_manager_reraises():
                        raise exc_gen()
                
                self.assertEqual(cm.exception.message, exc_example.message)
            
            with self.subTest("Context manager raises from:", exc_type=exc_type.__name__):
                @contextlib.contextmanager
                def context_manager_raises_from():
                    try:
                        yield
                    except Exception as e:
                        raise exc_gen() from e
                
                with self.assertRaises(exc_type) as cm:
                    with context_manager_raises_from():
                        raise Exception("message")
                
                self.assertEqual(cm.exception.message, exc_example.message)
            
            with self.subTest("Context manager suppresses:", exc_type=exc_type.__name__):
                @contextlib.contextmanager
                def context_manager_suppresses():
                    try:
                        yield
                    except exc_type:
                        pass
                
                with context_manager_suppresses():
                    raise exc_gen()
    
    def test_can_warning(self):
        @dataclassabc(frozen=True)
        class DerivedWarning(BaseExceptionABC, Warning):
            message: str
        
        with self.assertWarns(DerivedWarning) as cm:
            warnings.warn(DerivedWarning("warning message"))
        self.assertEqual(cm.warning.message, "warning message")
    
    def test_can_subclass(self):
        with self.subTest("Field form (@dataclassabc)"):
            @dataclassabc(frozen=True)
            class DerivedExceptionWithField(BaseExceptionABC):
                message: str
            
            with self.assertRaises(DerivedExceptionWithField) as cm:
                raise DerivedExceptionWithField("custom message")
            self.assertEqual(cm.exception.message, "custom message")
        
        with self.subTest("Property form (@dataclass)"):
            @dataclass(frozen=True)
            class DerivedExceptionWithProperty(BaseExceptionABC):
                @property
                def message(self) -> str:
                    return "custom message 101"
            
            with self.assertRaises(DerivedExceptionWithProperty) as cm:
                raise DerivedExceptionWithProperty
            self.assertEqual(cm.exception.message, "custom message 101")
        
        with self.subTest("Field form (@dataclass_exception)"):
            @dataclass_exception
            class DerivedExceptionWithField(BaseExceptionABC):
                message: str
            
            with self.assertRaises(DerivedExceptionWithField) as cm:
                raise DerivedExceptionWithField("custom message")
            self.assertEqual(cm.exception.message, "custom message")
        
        with self.subTest("Property form (@dataclass_exception)"):
            @dataclass_exception
            class DerivedExceptionWithProperty(BaseExceptionABC):
                @property
                def message(self) -> str:
                    return "custom message 101"
            
            with self.assertRaises(DerivedExceptionWithProperty) as cm:
                raise DerivedExceptionWithProperty
            self.assertEqual(cm.exception.message, "custom message 101")



if (__name__ == '__main__'):
    from unittest import main
    main()
