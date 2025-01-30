"""Type stubs for pydantic_settings."""
from typing import Any, Dict, Optional, Union

from ..pydantic import BaseModel

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