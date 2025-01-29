"""Type stubs for pandas."""
from typing import Any, Dict, List, Optional, TypeVar, Union, overload

T = TypeVar('T')

class DataFrame:
    def __init__(self, data: Optional[Union[Dict[str, List[Any]], List[Dict[str, Any]]]] = None) -> None: ...
    
    @overload
    def to_dict(self, orient: str = "dict") -> Dict[str, Any]: ...
    
    @overload
    def to_dict(self, orient: str = "records") -> List[Dict[str, Any]]: ... 