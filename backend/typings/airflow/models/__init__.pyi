"""Type stubs for airflow.models."""
from typing import Any, Optional, Union, Sequence

class BaseOperator:
    def __init__(
        self,
        task_id: str,
        dag: Optional[Any] = None,
        **kwargs: Any,
    ) -> None: ...
    
    def set_downstream(self, task_or_tasks: Union["BaseOperator", Sequence["BaseOperator"]]) -> None: ... 