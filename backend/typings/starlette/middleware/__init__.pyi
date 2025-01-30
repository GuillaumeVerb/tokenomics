"""Type stubs for starlette.middleware."""
from typing import Any, Callable, Dict, Optional, Sequence, Type, Union

from ..types import ASGIApp, Receive, Scope, Send

class Middleware:
    def __init__(
        self,
        cls: Type["BaseHTTPMiddleware"],
        **options: Any,
    ) -> None: ...

class BaseHTTPMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        dispatch: Optional[Callable[..., Any]] = None,
    ) -> None: ...
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
    
    async def dispatch(
        self,
        request: Any,
        call_next: Callable[..., Any],
    ) -> Any: ... 