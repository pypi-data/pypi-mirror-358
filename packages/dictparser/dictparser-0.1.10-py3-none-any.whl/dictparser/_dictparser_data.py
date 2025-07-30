import typing


CLASS_DATA_FIELD_NAME = "__dictparser_class_data__"
TYPE_INFO_FIELD_NAME = "__dictparser_type_info__"


class MISSING:  # pylint: disable=too-few-public-methods
    pass


class Field:
    def __init__(
        self,
        field_name,
        field_type,
        data_key,
        default: typing.Any = MISSING,
        default_factory: typing.Any = MISSING
    ):  # pylint: disable=too-many-arguments
        self._field_name = field_name
        self._field_type = field_type
        self._data_key = data_key
        self._default = None
        self._default_factory = None
        self._has_default = False
        self._required = True

        if default is not MISSING and default_factory is not MISSING:
            raise RuntimeError("Can not provide both default and default_factory in the same field")

        if default is not MISSING:
            self._has_default = True
            self._required = False
            self._default = default

        if default_factory is not MISSING:
            self._has_default = True
            self._required = False
            self._default_factory = default_factory

    def get_default_value(self):
        if self._default_factory:
            return self._default_factory()
        else:
            return self._default

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def field_type(self):
        return self._field_type

    @property
    def data_key(self) -> str:
        return self._data_key

    @property
    def has_default(self) -> bool:
        return self._has_default

    @property
    def is_required(self) -> bool:
        return self._required


class ClassData:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.result_cls: typing.Type = None  # type: ignore # This is to solve a chicken egg problem. It should always be non null for most of the code
        self.field_defaults: dict[str, typing.Any] = {}
        self.data_resolver: typing.Callable[['ClassData'],'ResolvedClassData'] | None = None
        self._resolved_data: 'ResolvedClassData | None' = None

    @property
    def resolved_data(self) -> 'ResolvedClassData':
        if self._resolved_data is None:
            if self.data_resolver is not None:
                self._resolved_data = self.data_resolver(self)
            else:
                raise RuntimeError("Internal Error. Missing ClassData resolver method")

        return self._resolved_data


class ResolvedClassData:  # pylint: disable=too-few-public-methods
    def __init__(self, result_cls: typing.Type):
        self.result_cls = result_cls
        self.fields: typing.Dict[str, Field] = {}
        self.has_required: bool = False
        self.ignore_extra: bool = False


class TypeInfo:  # pylint: disable=too-few-public-methods
    def __init__(self, parent, cls: typing.Type, data_key: str):
        self.parent: TypeInfo | None = parent
        self.cls = cls
        self.data_key = data_key
        self.type_name: typing.Optional[str] = None
        self.children: typing.Dict[str, TypeInfo] = {}
