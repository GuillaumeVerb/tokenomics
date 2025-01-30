"""Type stubs for FastAPI routing."""
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from starlette.responses import Response
from starlette.routing import BaseRoute

class APIRouter:
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[Sequence[Any]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        default_response_class: Type[Response] = Response,
        routes: Optional[List[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[Any] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Optional[Any] = None,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Optional[Callable[[Any], str]] = None,
    ) -> None: ...

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
        response_class: Type[Response] = Response,
        name: Optional[str] = None,
    ) -> Callable: ...

    def post(self, path: str, **kwargs: Any) -> Callable: ...
    def put(self, path: str, **kwargs: Any) -> Callable: ...
    def delete(self, path: str, **kwargs: Any) -> Callable: ...
    def options(self, path: str, **kwargs: Any) -> Callable: ...
    def head(self, path: str, **kwargs: Any) -> Callable: ...
    def patch(self, path: str, **kwargs: Any) -> Callable: ...
    def trace(self, path: str, **kwargs: Any) -> Callable: ... 