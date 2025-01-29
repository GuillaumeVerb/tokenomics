"""Type stubs for FastAPI."""
from typing import Any, Callable, Dict, List, Optional, Type, Union

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

class FastAPI(Starlette):
    def __init__(
        self,
        *,
        debug: bool = False,
        routes: Optional[List[BaseRoute]] = None,
        title: str = "FastAPI",
        description: str = "",
        version: str = "0.1.0",
        openapi_url: Optional[str] = "/openapi.json",
        openapi_tags: Optional[List[Dict[str, Any]]] = None,
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
        middleware: Optional[List[Middleware]] = None,
        **extra: Any,
    ) -> None: ...

    def get(
        self,
        path: str,
        *,
        response_model: Optional[Type[Any]] = None,
        status_code: Optional[int] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        **kwargs: Any,
    ) -> Callable[..., Any]: ...

    def post(
        self,
        path: str,
        *,
        response_model: Optional[Type[Any]] = None,
        status_code: Optional[int] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        **kwargs: Any,
    ) -> Callable[..., Any]: ... 