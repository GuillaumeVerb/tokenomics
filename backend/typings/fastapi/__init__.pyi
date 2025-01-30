"""Type stubs for FastAPI."""
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from .responses import Response
from .routing import APIRouter
from ..starlette.middleware.base import Request
from ..starlette.applications import Starlette
from ..starlette.middleware import Middleware
from ..starlette.routing import BaseRoute
from ..starlette.types import ASGIApp, Receive, Scope, Send

class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

class FastAPI(Starlette):
    def __init__(
        self,
        *,
        debug: bool = False,
        routes: Optional[Sequence[BaseRoute]] = None,
        title: str = "FastAPI",
        description: str = "",
        version: str = "0.1.0",
        openapi_url: Optional[str] = "/openapi.json",
        openapi_tags: Optional[List[Dict[str, Any]]] = None,
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
        middleware: Optional[Sequence[Middleware]] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], Callable]] = None,
        on_startup: Optional[Sequence[Callable]] = None,
        on_shutdown: Optional[Sequence[Callable]] = None,
        terms_of_service: Optional[str] = None,
        contact: Optional[Dict[str, Union[str, Any]]] = None,
        license_info: Optional[Dict[str, Union[str, Any]]] = None,
        openapi_prefix: str = "",
        root_path: str = "",
        root_path_in_servers: bool = True,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc",
        swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
        swagger_ui_init_oauth: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

    def get(
        self,
        path: str,
        *,
        response_model: Optional[Type[Any]] = None,
        status_code: Optional[int] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[Sequence[Any]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        include_in_schema: bool = True,
        response_class: Optional[Type[Any]] = None,
        name: Optional[str] = None,
    ) -> Callable: ...

    def post(self, path: str, **kwargs: Any) -> Callable: ...
    def put(self, path: str, **kwargs: Any) -> Callable: ...
    def delete(self, path: str, **kwargs: Any) -> Callable: ...
    def options(self, path: str, **kwargs: Any) -> Callable: ...
    def head(self, path: str, **kwargs: Any) -> Callable: ...
    def patch(self, path: str, **kwargs: Any) -> Callable: ...
    def trace(self, path: str, **kwargs: Any) -> Callable: ...

    def include_router(
        self,
        router: Any,
        *,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[Sequence[Any]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        default_response_class: Optional[Type[Any]] = None,
        callbacks: Optional[List[Any]] = None,
        generate_unique_id_function: Optional[Callable[[Any], str]] = None,
    ) -> None: ...

    def middleware(self, middleware_type: str) -> Callable: ...
    def exception_handler(self, exc_class_or_status_code: Union[Type[Exception], int]) -> Callable: ...
    def on_event(self, event_type: str) -> Callable: ...

__all__ = ['FastAPI', 'HTTPException', 'Request', 'Response', 'APIRouter'] 