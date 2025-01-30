"""Type stubs for starlette."""
from typing import Any, Dict, Optional, Sequence, Type, Union

from .middleware import BaseHTTPMiddleware, Middleware
from .responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from .routing import BaseRoute, Mount, Route, Router, WebSocketRoute
from .types import ASGIApp, Message, Receive, Scope, Send

__all__ = [
    "Starlette",
    "BaseHTTPMiddleware",
    "Middleware",
    "Response",
    "HTMLResponse",
    "JSONResponse",
    "PlainTextResponse",
    "RedirectResponse",
    "BaseRoute",
    "Route",
    "WebSocketRoute",
    "Mount",
    "Router",
    "ASGIApp",
    "Message",
    "Receive",
    "Scope",
    "Send",
]

class Starlette:
    def __init__(
        self,
        debug: bool = False,
        routes: Optional[Sequence[BaseRoute]] = None,
        middleware: Optional[Sequence[Middleware]] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], Any]] = None,
        on_startup: Optional[Sequence[Any]] = None,
        on_shutdown: Optional[Sequence[Any]] = None,
        lifespan: Optional[Any] = None,
    ) -> None: ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
    
    @property
    def routes(self) -> Sequence[BaseRoute]: ...
    
    @property
    def middleware(self) -> Sequence[Middleware]: ...
    
    def url_path_for(self, name: str, **path_params: Any) -> str: ...
    
    def mount(
        self,
        path: str,
        app: ASGIApp,
        name: Optional[str] = None,
    ) -> None: ...
    
    def host(
        self,
        host: str,
        app: ASGIApp,
        name: Optional[str] = None,
    ) -> None: ...
    
    def add_middleware(self, middleware_class: Type[Middleware], **options: Any) -> None: ...
    
    def add_exception_handler(
        self,
        exc_class_or_status_code: Union[int, Type[Exception]],
        handler: Any,
    ) -> None: ...
    
    def add_event_handler(self, event_type: str, func: Any) -> None: ...
    
    def add_route(
        self,
        path: str,
        route: Any,
        methods: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None: ... 