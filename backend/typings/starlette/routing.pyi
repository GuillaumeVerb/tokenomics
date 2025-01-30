"""Type stubs for starlette.routing."""
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from .types import ASGIApp, Receive, Scope, Send

class BaseRoute:
    def matches(self, scope: Scope) -> bool: ...
    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None: ...

class Route(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None: ...

class WebSocketRoute(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: Optional[str] = None,
    ) -> None: ...

class Mount(BaseRoute):
    def __init__(
        self,
        path: str,
        app: ASGIApp,
        name: Optional[str] = None,
    ) -> None: ...

class Router:
    def __init__(
        self,
        routes: Optional[Sequence[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        on_startup: Optional[Sequence[Callable]] = None,
        on_shutdown: Optional[Sequence[Callable]] = None,
        lifespan: Optional[Callable[["Router"], Any]] = None,
    ) -> None: ...
    
    def url_path_for(self, name: str, **path_params: Any) -> str: ...
    
    def add_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None: ...
    
    def add_websocket_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        name: Optional[str] = None,
    ) -> None: ...
    
    def mount(
        self,
        path: str,
        app: ASGIApp,
        name: Optional[str] = None,
    ) -> None: ... 