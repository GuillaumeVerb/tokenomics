"""Type stubs for pydantic."""
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable, ClassVar, overload, Generic, Tuple, Literal, get_args, get_origin
from typing_extensions import Annotated, TypeAlias
from decimal import Decimal

_T = TypeVar("_T")
_FieldType = TypeVar("_FieldType")

class ConfigDict(Dict[str, Any]):
    @staticmethod
    def __new__(cls, *args: Any, **kwargs: Any) -> "ConfigDict": ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

def computed_field() -> Any: ...

def field_validator(
    __field: str,
    *fields: str,
    mode: str = "after",
    check_fields: Optional[bool] = None,
) -> Callable[[Any], Any]: ...

def model_validator(
    mode: str = "after",
) -> Callable[[Any], Any]: ...

class Field(Generic[_FieldType]):
    @overload
    def __init__(
        self,
        default: _FieldType,
        *,
        default_factory: None = None,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        exclude: Optional[bool] = None,
        include: Optional[bool] = None,
        const: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        discriminator: Optional[str] = None,
        repr: bool = True,
        json_schema_extra: Optional[Dict[str, Any]] = None,
        frozen: Optional[bool] = None,
        validate_default: Optional[bool] = None,
        **extra: Any,
    ) -> None: ...
    
    @overload
    def __init__(
        self,
        *,
        default_factory: Callable[[], _FieldType],
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        exclude: Optional[bool] = None,
        include: Optional[bool] = None,
        const: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        discriminator: Optional[str] = None,
        repr: bool = True,
        json_schema_extra: Optional[Dict[str, Any]] = None,
        frozen: Optional[bool] = None,
        validate_default: Optional[bool] = None,
        **extra: Any,
    ) -> None: ...
    
    def __get__(self, obj: Optional[Any], owner: Any) -> _FieldType: ...
    def __set__(self, obj: Any, value: _FieldType) -> None: ...

class BaseModel:
    model_config: ClassVar[ConfigDict]

    def __init__(self, **data: Any) -> None: ...
    
    def model_dump(
        self,
        *,
        mode: str = "python",
        include: Optional[Union[set[str], dict[str, Any]]] = None,
        exclude: Optional[Union[set[str], dict[str, Any]]] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> Dict[str, Any]: ...
    
    def model_dump_json(
        self,
        *,
        indent: Optional[int] = None,
        include: Optional[Union[set[str], dict[str, Any]]] = None,
        exclude: Optional[Union[set[str], dict[str, Any]]] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str: ...
    
    @classmethod
    def model_validate(
        cls: Type[_T],
        obj: Any,
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> _T: ...
    
    @classmethod
    def model_validate_json(
        cls: Type[_T],
        json_data: Union[str, bytes],
        *,
        strict: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> _T: ...
    
    def model_copy(
        self: _T,
        *,
        update: Optional[Dict[str, Any]] = None,
        deep: bool = False,
    ) -> _T: ...
    
    # Backwards compatibility aliases
    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]: ...
    def json(self, *args: Any, **kwargs: Any) -> str: ...
    @classmethod
    def parse_obj(cls: Type[_T], obj: Any) -> _T: ...
    @classmethod
    def parse_raw(cls: Type[_T], b: Union[str, bytes], **kwargs: Any) -> _T: ...
    @classmethod
    def parse_file(cls: Type[_T], path: Union[str, bytes], **kwargs: Any) -> _T: ...
    @classmethod
    def from_orm(cls: Type[_T], obj: Any) -> _T: ...
    
    class Config:
        title: Optional[str] = None
        str_to_lower: bool = False
        str_to_upper: bool = False
        str_strip_whitespace: bool = False
        str_min_length: int = 0
        str_max_length: Optional[int] = None
        extra: str = "ignore"
        frozen: bool = False
        populate_by_name: bool = False
        use_enum_values: bool = False
        validate_assignment: bool = False
        arbitrary_types_allowed: bool = False
        from_attributes: bool = False
        loc_by_alias: bool = True
        alias_generator: Optional[Callable[[str], str]] = None
        ignored_types: tuple[Type[Any], ...] = ()
        allow_inf_nan: bool = True
        json_schema_extra: Optional[Union[Dict[str, Any], Callable[..., None]]] = None
        json_encoders: Optional[Dict[Type[Any], Callable[[Any], Any]]] = None
        underscore_attrs_are_private: bool = False

class BaseSettings(BaseModel):
    class Config:
        env_prefix: str = ""
        env_file: Optional[str] = None
        env_file_encoding: str = "utf8"
        env_nested_delimiter: str = "__"
        env_file_path: Optional[Union[str, list[str]]] = None
        secrets_dir: Optional[str] = None
        case_sensitive: bool = False
        env_ignore_empty: bool = False
        validate_default: bool = True
        extra: str = "ignore"
        arbitrary_types_allowed: bool = False
        env_parse_none: bool = False
        env_parse_empty: bool = False
        env_keep_json: bool = False
        env_json_loads: Any = None
        env_json_dumps: Any = None
        env_json_serializer: Any = None
        env_json_deserializer: Any = None
        env_json_schema: Dict[str, Any] = {}

# Type aliases for common field types
DecimalField: TypeAlias = Field[Decimal]
IntField: TypeAlias = Field[int]
StrField: TypeAlias = Field[str]
BoolField: TypeAlias = Field[bool]
ListField: TypeAlias = Field[List[Any]]
DictField: TypeAlias = Field[Dict[str, Any]]

__all__ = [
    'BaseModel',
    'BaseSettings',
    'ConfigDict',
    'Field',
    'DecimalField',
    'IntField',
    'StrField',
    'BoolField',
    'ListField',
    'DictField',
    'computed_field',
    'field_validator',
    'model_validator',
] 