"""Type stubs for requests."""
from typing import Any, Dict, Optional, Union, Mapping, Sequence

class Response:
    status_code: int
    text: str
    content: bytes
    headers: Mapping[str, str]
    encoding: Optional[str]
    url: str
    
    def json(self, **kwargs: Any) -> Any: ...
    def raise_for_status(self) -> None: ...

class Session:
    def get(
        self,
        url: str,
        params: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
        **kwargs: Any,
    ) -> Response: ...
    
    def post(
        self,
        url: str,
        data: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response: ...
    
    def put(
        self,
        url: str,
        data: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
        **kwargs: Any,
    ) -> Response: ...
    
    def delete(
        self,
        url: str,
        **kwargs: Any,
    ) -> Response: ...

def get(
    url: str,
    params: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
    **kwargs: Any,
) -> Response: ...

def post(
    url: str,
    data: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
    json: Optional[Any] = None,
    **kwargs: Any,
) -> Response: ...

def put(
    url: str,
    data: Optional[Union[Mapping[str, Any], Sequence[tuple[str, Any]]]] = None,
    **kwargs: Any,
) -> Response: ...

def delete(
    url: str,
    **kwargs: Any,
) -> Response: ... 