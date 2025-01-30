"""Type stubs for starlette.types."""
from typing import Any, Callable, Dict, Union, Protocol, TypeVar, Sequence, Optional

Message = Dict[str, Any]
Scope = Dict[str, Any]
Receive = Callable[[], Message]
Send = Callable[[Message], None]

ASGIApp = Callable[[Scope, Receive, Send], None]

class Buffer(Protocol):
    def __bytes__(self) -> bytes: ...

ReadableBuffer = Union[bytes, bytearray, memoryview, Buffer]

class BytesLike:
    def __init__(self, value: Union[str, bytes]) -> None: ...
    def startswith(self, prefix: Union[str, bytes, Sequence[Union[str, bytes]]]) -> bool: ...
    def split(self, sep: Optional[Union[str, bytes]] = None, maxsplit: int = -1) -> list[bytes]: ...
    def decode(self, encoding: str = "utf-8", errors: str = "strict") -> str: ...
    def __bytes__(self) -> bytes: ... 