"""Type stubs for FastAPI responses."""
from typing import Any, Dict, Optional, Union

from starlette.responses import Response as StarletteResponse

class Response(StarletteResponse):
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None: ...

class JSONResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "application/json",
        background: Optional[Any] = None,
    ) -> None: ...

class HTMLResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/html",
        background: Optional[Any] = None,
    ) -> None: ...

class PlainTextResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/plain",
        background: Optional[Any] = None,
    ) -> None: ...

class RedirectResponse(Response):
    def __init__(
        self,
        url: str,
        status_code: int = 307,
        headers: Optional[Dict[str, str]] = None,
        background: Optional[Any] = None,
    ) -> None: ... 