import dataclasses
import copy
import sys

from typing import get_type_hints

from .mapper import Mapper
from ._dictparser_data import MISSING, Field
from ._dictparser_data import CLASS_DATA_FIELD_NAME, ClassData, ResolvedClassData
from ._dictparser_data import TYPE_INFO_FIELD_NAME, TypeInfo
from ._type_utils import setattr_method, setattr_classmethod


_default_mapper = Mapper()


def from_dict(cls, data):
    return _default_mapper.from_dict(cls, data)


def from_file(cls, file):
    return _default_mapper.from_file(cls, file)


def as_dict(value):
    return _default_mapper.as_dict(value)


def to_dict(value):
    return _default_mapper.as_dict(value)


def get_fields(class_or_instance):
    data = getattr(class_or_instance, CLASS_DATA_FIELD_NAME, None)
    if data is None:
        raise TypeError("Value needs to be a class created by dictparser or be an instance of such a class")

    return tuple(data.resolved_data.fields.values())


def process_class(cls, **kargs):
    if sys.version_info >= (3, 10):
        set_cls_defaults = True
    else:
        set_cls_defaults = False
        if "kw_only" in kargs:
            del kargs["kw_only"]

    #
    #
    #
    _class_data = ClassData()
    _class_data.data_resolver = calculate_resolved_class_data

    if hasattr(cls, "__annotations__"):
        for field_name in cls.__annotations__:
            default = MISSING
            default_factory = MISSING

            if hasattr(cls, field_name):
                default = getattr(cls, field_name)

                if not set_cls_defaults:
                    delattr(cls, field_name)

            if default is not MISSING:
                _class_data.field_defaults[field_name] = default

                if default.__class__.__hash__ is None:
                    default = MISSING
                    default_factory = _make_default_factory_for_dataclass(cls, _class_data, field_name)

            if set_cls_defaults:
                if default is not MISSING:
                    setattr(cls, field_name, default)

                elif default_factory is not MISSING:
                    setattr(cls, field_name, dataclasses.field(default_factory=default_factory))  # pylint: disable=:invalid-field-call

                elif hasattr(cls, field_name):
                    delattr(cls, field_name)

    cls = _class_data.result_cls = dataclasses.dataclass(**kargs)(cls)

    setattr(cls, CLASS_DATA_FIELD_NAME, _class_data)

    #
    #
    #
    setattr_classmethod(cls, "from_dict", from_dict)
    setattr_classmethod(cls, "from_file", from_file)
    setattr_method(cls, "to_dict", to_dict)
    setattr_method(cls, "as_dict", as_dict)

    return cls


def process_type_info(cls, data_key = None, type_name = None):
    parent = getattr(cls, TYPE_INFO_FIELD_NAME, None)

    if parent is None:
        if data_key is None:
            effective_data_key = "@type"
        else:
            effective_data_key = data_key
    else:
        if data_key is None:
            effective_data_key = parent.data_key
        else:
            raise RuntimeError("Can not have both a parent and set data_key value")

    v_type_info = TypeInfo(parent, cls, effective_data_key)
    v_type_info.type_name = type_name

    if type_name is not None:
        current = v_type_info
        while current is not None:
            current.children[type_name] = v_type_info
            current = current.parent

    setattr(cls, TYPE_INFO_FIELD_NAME, v_type_info)
    return cls


def calculate_resolved_class_data(class_data):
    res = ResolvedClassData(class_data.result_cls)

    for base in class_data.result_cls.__mro__[-1:0:-1]:
        base_data = getattr(base, CLASS_DATA_FIELD_NAME, None)
        if base_data is not None:
            for field in base_data.resolved_data.fields.values():
                res.fields[field.field_name] = field

    if hasattr(class_data.result_cls, "__annotations__"):
        type_hints = get_type_hints(class_data.result_cls)

        for field_name in class_data.result_cls.__annotations__:
            default = class_data.field_defaults.get(field_name, MISSING)
            default_factory = MISSING
            field_type = type_hints[field_name]

            if default is not MISSING:
                default = _default_mapper.get_converter_for_type(field_type).convert_value(default)

                if default.__class__.__hash__ is None:
                    def copy_factory(default):
                        return lambda : copy.deepcopy(default)

                    default_factory = copy_factory(default)
                    default = MISSING

                    default_factory.__qualname__ = f"{class_data.result_cls.__qualname__}.__deepcopy_{field_name}_default_value__"

            res.fields[field_name] = Field(field_name, field_type, field_name, default, default_factory)

    for field in res.fields.values():
        if not field.has_default:
            res.has_required = True
            break

    return res


def _make_default_factory_for_dataclass(cls, class_data, field_name):
    def default_factory():
        return class_data.resolved_data.fields[field_name].get_default_value()

    default_factory.__qualname__ = f"{cls.__qualname__}.__deepcopy_{field_name}_default_value__"

    return default_factory
