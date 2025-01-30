"""Type stubs for starlette.middleware.httpsredirect."""
from typing import Any

from ..types import ASGIApp, Receive, Scope, Send

class HTTPSRedirectMiddleware:
    def __init__(self, app: ASGIApp) -> None: ...
    
    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None: ... 