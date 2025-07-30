# pylint: disable=R0801
import typing


def type_get_origin(t):
    if hasattr(t, "__origin__"):
        return t.__origin__
    else:
        return None


def type_get_args(t):
    return list(t.__args__)


def is_union_type(t):
    origin = type_get_origin(t)
    return origin in (typing.Union, )
