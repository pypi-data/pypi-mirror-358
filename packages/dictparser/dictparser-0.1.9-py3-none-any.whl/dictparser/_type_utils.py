__all__ = ['type_get_origin', 'type_get_args', 'is_union_type', 'setattr_method', 'setattr_classmethod', 'strip_generic_from_type']

import sys

if sys.version_info >= (3, 10):
    from ._type_utils_p310 import type_get_origin, type_get_args, is_union_type
else:
    from ._type_utils_p36 import type_get_origin, type_get_args, is_union_type


def setattr_method(cls, method_name, func):
    if hasattr(cls, method_name):
        return

    def func_wrapper(*args, **kargs):
        return func(*args, **kargs)

    func_wrapper.__qualname__ = f"{cls.__qualname__}.{method_name}"

    setattr(cls, method_name, func_wrapper)


def setattr_classmethod(cls, method_name, func):
    if hasattr(cls, method_name):
        return

    def func_wrapper(*args, **kargs):
        return func(*args, **kargs)

    func_wrapper.__qualname__ = f"{cls.__qualname__}.{method_name}"

    setattr(cls, method_name, classmethod(func_wrapper))


def strip_generic_from_type(vtype):
    vtype_origin = type_get_origin(vtype)
    if vtype_origin is None:
        return vtype
    else:
        return vtype_origin
