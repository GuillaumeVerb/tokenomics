"""Type stubs for pytest."""
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, overload

_T = TypeVar("_T")
_F = TypeVar("_F", bound=Callable[..., Any])

@overload
def fixture(
    callable_or_scope: _F,
    *,
    scope: str = "function",
    params: Optional[List[Any]] = None,
    autouse: bool = False,
    ids: Optional[Union[List[str], Callable[[Any], str]]] = None,
    name: Optional[str] = None,
) -> _F: ...

@overload
def fixture(
    *,
    scope: str = "function",
    params: Optional[List[Any]] = None,
    autouse: bool = False,
    ids: Optional[Union[List[str], Callable[[Any], str]]] = None,
    name: Optional[str] = None,
) -> Callable[[_F], _F]: ...

def mark(
    name: str,
    *args: Any,
    **kwargs: Any,
) -> Any: ...

def raises(
    expected_exception: Union[Type[BaseException], tuple[Type[BaseException], ...]],
    *,
    match: Optional[str] = None,
) -> Any: ...

def skip(reason: str = "") -> None: ...
def fail(msg: str = "", pytrace: bool = True) -> None: ...

class MonkeyPatch:
    def setattr(self, target: Any, name: str, value: Any, raising: bool = True) -> None: ...
    def delattr(self, target: Any, name: str, raising: bool = True) -> None: ...
    def setitem(self, dic: Dict[Any, Any], name: Any, value: Any) -> None: ...
    def delitem(self, dic: Dict[Any, Any], name: Any, raising: bool = True) -> None: ...
    def setenv(self, name: str, value: str, prepend: Optional[str] = None) -> None: ...
    def delenv(self, name: str, raising: bool = True) -> None: ...
    def syspath_prepend(self, path: str) -> None: ...
    def chdir(self, path: str) -> None: ...
    def undo(self) -> None: ... 