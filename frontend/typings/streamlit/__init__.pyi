"""Type stubs for streamlit."""
from typing import Any, Optional, Union, Sequence, Callable, TypeVar

T = TypeVar('T')

def title(text: str) -> None: ...
def header(text: str) -> None: ...
def subheader(text: str) -> None: ...
def text(text: Any) -> None: ...
def markdown(text: str) -> None: ...

def sidebar() -> 'DeltaGenerator': ...

def dataframe(data: Any, width: Optional[int] = None, height: Optional[int] = None) -> None: ...
def table(data: Any) -> None: ...

def selectbox(
    label: str,
    options: Sequence[T],
    index: int = 0,
    key: Optional[str] = None,
) -> T: ...

def button(
    label: str,
    key: Optional[str] = None,
    help: Optional[str] = None,
) -> bool: ...

def download_button(
    label: str,
    data: Union[str, bytes],
    file_name: str,
    mime: Optional[str] = None,
    key: Optional[str] = None,
) -> bool: ...

def plotly_chart(
    figure_or_data: Any,
    use_container_width: bool = False,
    **kwargs: Any,
) -> None: ...

class DeltaGenerator:
    def title(self, text: str) -> None: ...
    def header(self, text: str) -> None: ...
    def subheader(self, text: str) -> None: ...
    def text(self, text: Any) -> None: ...
    def markdown(self, text: str) -> None: ...
    def selectbox(
        self,
        label: str,
        options: Sequence[T],
        index: int = 0,
        key: Optional[str] = None,
    ) -> T: ... 
