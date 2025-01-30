"""Type stubs for pandas."""
from typing import Any, Dict, List, Optional, Sequence, TypeVar, Union, overload, Callable, Generic, Literal

T = TypeVar('T')

class _iLocIndexer(Generic[T]):
    def __getitem__(self, key: Any) -> T: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class _LocIndexer(Generic[T]):
    def __getitem__(self, key: Any) -> T: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class Styler:
    def background_gradient(
        self,
        cmap: Optional[str] = None,
        low: float = 0,
        high: float = 0,
        axis: Optional[int] = 0,
        subset: Optional[Any] = None,
        text_color_threshold: float = 0.408,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        gmap: Optional[Any] = None,
    ) -> 'Styler': ...

class DataFrame:
    @overload
    def __init__(
        self, 
        data: Optional[Any] = None,
        index: Optional[Union[Sequence, Any]] = None,
        columns: Optional[Union[Sequence, Any]] = None,
        dtype: Optional[Any] = None,
        copy: Optional[bool] = None,
    ) -> None: ...
    
    @overload
    def __init__(self, data: Dict[str, Any], **kwargs: Any) -> None: ...
    
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    
    @property
    def iloc(self) -> _iLocIndexer[Any]: ...
    
    @property
    def loc(self) -> _LocIndexer[Any]: ...
    
    @property
    def style(self) -> Styler: ...
    
    def to_csv(
        self,
        path_or_buf: Optional[str] = None,
        sep: str = ",",
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        header: Union[bool, list[str]] = True,
        index: bool = True,
        index_label: Optional[Union[str, Sequence[str]]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
        compression: Union[str, dict[str, Any]] = "infer",
        quoting: Optional[int] = None,
        quotechar: str = '"',
        lineterminator: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        doublequote: bool = True,
        escapechar: Optional[str] = None,
        decimal: str = ".",
        errors: str = "strict",
        storage_options: Optional[dict[str, Any]] = None,
    ) -> Optional[str]: ...

def read_csv(
    filepath_or_buffer: Union[str, Any],
    sep: str = ",",
    delimiter: Optional[str] = None,
    header: Union[int, Sequence[int], None, Literal["infer"]] = "infer",
    names: Optional[Sequence[str]] = None,
    index_col: Optional[Union[int, str, Sequence[Union[int, str]]]] = None,
    usecols: Optional[Union[Sequence[str], Sequence[int]]] = None,
    dtype: Optional[Union[str, Dict[str, Any]]] = None,
    engine: Optional[str] = None,
    encoding: Optional[str] = None,
    **kwargs: Any,
) -> DataFrame: ...

# Factory function
def __dataframe_constructor(
    data: Optional[Union[Dict[str, List[Any]], List[Dict[str, Any]], Sequence[Any]]] = None,
    **kwargs: Any,
) -> DataFrame: ... 