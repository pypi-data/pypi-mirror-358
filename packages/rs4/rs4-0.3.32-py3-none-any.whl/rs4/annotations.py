import warnings
import copy
from functools import wraps
from abc import ABCMeta, abstractmethod

Abstract = ABCMeta


def copy_class (cls):
    copy_cls = type (f'{cls.__name__}Copy', cls.__bases__, dict (cls.__dict__))
    for name, attr in cls.__dict__.items ():
        try:
            hash (attr)
        except TypeError:
            setattr (copy_cls, name, copy.deepcopy (attr))
    return copy_cls

class Uninstalled:
    def __init__ (self, name, libname = None):
        self.name = name
        self.libname = libname or name

    def __call__ (self, *args, **kargs):
        raise ImportError ('cannot import {}, install first (pip install {})'.format (self.name, self.libname))


class Singleton (type):
    __instances = {}
    def __call__ (cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances [cls] = super ().__call__ (*args, **kwargs)
        return cls.__instances [cls]


def deprecated (msg = ""):
    def decorator (f):
        @wraps(f)
        def wrapper (*args, **kwargs):
            nonlocal msg

            warnings.simplefilter ('default')
            warnings.warn (
               "{} will be deprecated{}".format (f.__name__, msg and (", " + msg) or ""),
                DeprecationWarning
            )
            return f (*args, **kwargs)
        return wrapper

    if isinstance (msg, str):
        return decorator
    f, msg = msg, ''
    return decorator (f)

def override (f):
    @wraps (f)
    def wrapper (*args, **karg):
        return f (*args, **karg)
    return wrapper


class _ClassPropertyDescriptor:
    def __init__ (self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__ (self, obj, klass=None):
        if klass is None:
            klass = type (obj)
        return self.fget.__get__ (obj, klass)()

    def __set__ (self, obj, value):
        if not self.fset:
            raise AttributeError ("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__ (obj, type_)(value)

    def setter (self, func):
        if not isinstance (func, (classmethod, staticmethod)):
            func = classmethod (func)
        self.fset = func
        return self

def classproperty (func):
    if not isinstance (func, (classmethod, staticmethod)):
        func = classmethod (func)
    return _ClassPropertyDescriptor (func)

