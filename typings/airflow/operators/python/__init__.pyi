"""Type stubs for airflow.operators.python."""
from typing import Any, Callable, Dict, List, Optional

from airflow.models import BaseOperator

class PythonOperator(BaseOperator):
    def __init__(
        self,
        *,
        python_callable: Callable,
        op_args: Optional[List[Any]] = None,
        op_kwargs: Optional[Dict[str, Any]] = None,
        task_id: str,
        dag: Optional[Any] = None,
        **kwargs: Any
    ) -> None: ... 