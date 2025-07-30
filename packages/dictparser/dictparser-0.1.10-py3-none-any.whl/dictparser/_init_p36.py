# pylint: disable=R0801

__all__ = ['from_dict', 'from_file', 'as_dict', 'fields', 'Field', 'dictparser', 'type_info']

from ._dictparser_data import Field
from ._engine import from_dict as _from_dict
from ._engine import from_file as _from_file
from ._engine import to_dict as _to_dict
from ._engine import as_dict as _as_dict
from ._engine import get_fields as _get_fields
from ._engine import process_class as _process_class
from ._engine import process_type_info as _process_type_info


def from_dict(cls, data):
    return _from_dict(cls, data)


def from_file(cls, file):
    return _from_file(cls, file)


def to_dict(value):
    return _to_dict(value)


def as_dict(value):
    return _as_dict(value)


def fields(class_or_instance):
    return _get_fields(class_or_instance)


def dictparser(cls=None, **kargs):
    def wrap(cls):
        return _process_class(cls, **kargs)

    if cls is None:
        return wrap

    return wrap(cls)


def type_info(*, data_key = None, name = None):
    def type_info_wrapper(cls):
        return _process_type_info(cls, data_key, name)

    return type_info_wrapper
