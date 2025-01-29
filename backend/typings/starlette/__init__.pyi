"""Type stubs for Starlette."""
from typing import Any, Dict, List, Optional, Sequence, Type, Union

class Starlette:
    def __init__(
        self,
        debug: bool = False,
        routes: Optional[Sequence[Any]] = None,
        middleware: Optional[Sequence[Any]] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], Any]] = None,
        on_startup: Optional[Sequence[Any]] = None,
        on_shutdown: Optional[Sequence[Any]] = None,
        lifespan: Optional[Any] = None,
    ) -> None: ... 