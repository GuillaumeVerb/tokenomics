"""Type stubs for plotly.express."""
from typing import Any, Optional, Union, Sequence, Dict

from pandas import DataFrame

def line(
    data_frame: DataFrame,
    x: Optional[str] = None,
    y: Optional[Union[str, Sequence[str]]] = None,
    color: Optional[str] = None,
    line_group: Optional[str] = None,
    line_shape: Optional[str] = None,
    line_dash: Optional[str] = None,
    line_dash_sequence: Optional[Sequence[str]] = None,
    markers: Optional[bool] = None,
    title: Optional[str] = None,
    template: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    **kwargs: Any,
) -> Any: ...

def scatter(
    data_frame: DataFrame,
    x: Optional[str] = None,
    y: Optional[Union[str, Sequence[str]]] = None,
    color: Optional[str] = None,
    symbol: Optional[str] = None,
    size: Optional[str] = None,
    title: Optional[str] = None,
    template: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    **kwargs: Any,
) -> Any: ...

__all__ = ['line', 'scatter'] 