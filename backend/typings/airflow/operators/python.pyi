"""Type stubs for airflow.operators.python."""
from typing import Any, Callable, Dict, Optional, Sequence

from ..models import BaseOperator, DAG

class PythonOperator(BaseOperator):
    def __init__(
        self,
        *,
        python_callable: Callable[..., Any],
        op_args: Optional[Sequence[Any]] = None,
        op_kwargs: Optional[Dict[str, Any]] = None,
        templates_dict: Optional[Dict[str, Any]] = None,
        templates_exts: Optional[Sequence[str]] = None,
        provide_context: bool = False,
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ... 