"""Type stubs for airflow.operators.python."""
from typing import Any, Callable, Dict, Optional, Sequence

from airflow.models import BaseOperator

class PythonOperator(BaseOperator):
    def __init__(
        self,
        *,
        python_callable: Callable,
        op_args: Optional[Sequence] = None,
        op_kwargs: Optional[Dict] = None,
        templates_dict: Optional[Dict] = None,
        templates_exts: Optional[Sequence[str]] = None,
        provide_context: bool = False,
        task_id: str,
        dag: Optional[Any] = None,
        **kwargs: Any,
    ) -> None: ... 