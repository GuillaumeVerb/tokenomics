"""Type stubs for starlette.applications."""
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from .middleware import Middleware
from .routing import BaseRoute
from .types import ASGIApp, Receive, Scope, Send

class Starlette:
    def __init__(
        self,
        debug: bool = False,
        routes: Optional[Sequence[BaseRoute]] = None,
        middleware: Optional[Sequence[Middleware]] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], Callable]] = None,
        on_startup: Optional[Sequence[Callable]] = None,
        on_shutdown: Optional[Sequence[Callable]] = None,
        lifespan: Optional[Callable[["Starlette", Dict[str, Any]], Any]] = None,
    ) -> None: ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
    
    def url_path_for(self, name: str, **path_params: Any) -> str: ...
    
    def middleware(self, middleware_type: str) -> Callable: ...
    
    def exception_handler(
        self,
        exc_class_or_status_code: Union[int, Type[Exception]],
    ) -> Callable: ...
    
    def on_event(self, event_type: str) -> Callable: ...
    
    def mount(self, path: str, app: ASGIApp, name: Optional[str] = None) -> None: ...
    
    def host(self, host: str, app: ASGIApp, name: Optional[str] = None) -> None: ...
    
    def add_middleware(self, middleware_class: Type[Middleware], **options: Any) -> None: ...
    
    def add_exception_handler(
        self,
        exc_class_or_status_code: Union[int, Type[Exception]],
        handler: Callable,
    ) -> None: ...
    
    def add_event_handler(self, event_type: str, func: Callable) -> None: ...
    
    def add_route(
        self,
        path: str,
        route: Callable,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None: ...

# The Starlette class is defined in the main module
__all__ = [] 