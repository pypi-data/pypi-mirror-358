# pylint: disable=R0801
import typing
import types


def type_get_origin(t):
    return typing.get_origin(t)


def type_get_args(t):
    return list(typing.get_args(t))


def is_union_type(t):
    origin = type_get_origin(t)
    return origin in (types.UnionType, typing.Union)
