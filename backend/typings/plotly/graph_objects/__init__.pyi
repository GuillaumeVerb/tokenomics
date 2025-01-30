"""Type stubs for plotly.graph_objects."""
from typing import Any, Dict, List, Optional, Union, Sequence

class Figure:
    def __init__(
        self,
        data: Optional[Union[Dict[str, Any], Sequence[Dict[str, Any]]]] = None,
        layout: Optional[Dict[str, Any]] = None,
        frames: Optional[Sequence[Dict[str, Any]]] = None,
        skip_invalid: bool = False,
    ) -> None: ...
    
    def add_trace(
        self,
        trace: Union[Dict[str, Any], Any],
        row: Optional[int] = None,
        col: Optional[int] = None,
        secondary_y: bool = False,
    ) -> None: ...
    
    def update_layout(self, **kwargs: Any) -> None: ...
    def update_traces(self, **kwargs: Any) -> None: ...
    def update_xaxes(self, **kwargs: Any) -> None: ...
    def update_yaxes(self, **kwargs: Any) -> None: ...
    def to_json(self, **kwargs: Any) -> str: ...

class Scatter:
    def __init__(
        self,
        x: Optional[Sequence[Any]] = None,
        y: Optional[Sequence[Any]] = None,
        mode: Optional[str] = None,
        name: Optional[str] = None,
        line: Optional[Dict[str, Any]] = None,
        marker: Optional[Dict[str, Any]] = None,
        text: Optional[Union[str, Sequence[str]]] = None,
        **kwargs: Any,
    ) -> None: ...

class Bar:
    def __init__(
        self,
        x: Optional[Sequence[Any]] = None,
        y: Optional[Sequence[Any]] = None,
        name: Optional[str] = None,
        text: Optional[Union[str, Sequence[str]]] = None,
        **kwargs: Any,
    ) -> None: ...

class Line:
    def __init__(
        self,
        x: Optional[Sequence[Any]] = None,
        y: Optional[Sequence[Any]] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> None: ...

__all__ = ['Figure', 'Scatter', 'Bar', 'Line'] 