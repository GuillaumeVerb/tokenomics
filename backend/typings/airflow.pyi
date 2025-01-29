"""Type stubs for airflow."""
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

class DAG:
    def __init__(
        self,
        dag_id: str,
        description: Optional[str] = None,
        schedule_interval: Union[str, timedelta, None] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        default_args: Optional[Dict[str, Any]] = None,
        catchup: bool = True,
        **kwargs: Any,
    ) -> None: ...

class BaseOperator:
    def __init__(
        self,
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ...

class PythonOperator(BaseOperator):
    def __init__(
        self,
        *,
        python_callable: Callable,
        op_args: Optional[Sequence] = None,
        op_kwargs: Optional[Dict] = None,
        provide_context: bool = False,
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ...

class SimpleHttpOperator(BaseOperator):
    def __init__(
        self,
        *,
        endpoint: str,
        method: str = "POST",
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_filter: Optional[Callable[[Any], Any]] = None,
        http_conn_id: str = "http_default",
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ... 