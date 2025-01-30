"""Type stubs for airflow."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Sequence, Callable, Type

class DAG:
    def __init__(
        self,
        dag_id: str,
        description: Optional[str] = None,
        schedule_interval: Union[str, timedelta, None] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        full_filepath: Optional[str] = None,
        template_searchpath: Optional[Union[str, list[str]]] = None,
        template_undefined: Optional[Any] = None,
        user_defined_macros: Optional[Dict] = None,
        user_defined_filters: Optional[Dict] = None,
        default_args: Optional[Dict] = None,
        concurrency: Optional[int] = None,
        max_active_tasks: Optional[int] = None,
        dagrun_timeout: Optional[timedelta] = None,
        sla_miss_callback: Optional[Any] = None,
        default_view: Optional[str] = None,
        orientation: Optional[str] = None,
        catchup: bool = True,
        on_success_callback: Optional[Any] = None,
        on_failure_callback: Optional[Any] = None,
        doc_md: Optional[str] = None,
        params: Optional[Dict] = None,
        access_control: Optional[Dict] = None,
        is_paused_upon_creation: Optional[bool] = None,
        jinja_environment_kwargs: Optional[Dict] = None,
        render_template_as_native_obj: bool = False,
        tags: Optional[list[str]] = None,
    ) -> None: ...

class BaseOperator:
    def __init__(
        self,
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ...
    
    def set_downstream(self, task_or_tasks: Union['BaseOperator', Sequence['BaseOperator']]) -> None: ...

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

class SimpleHttpOperator(BaseOperator):
    def __init__(
        self,
        *,
        endpoint: str,
        method: str = "POST",
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_filter: Optional[Callable[[Any], Any]] = None,
        response_check: Optional[Callable[[Any], bool]] = None,
        extra_options: Optional[Dict[str, Any]] = None,
        http_conn_id: str = "http_default",
        log_response: bool = False,
        task_id: str,
        dag: Optional[DAG] = None,
        **kwargs: Any,
    ) -> None: ...

__all__ = ['DAG', 'BaseOperator', 'PythonOperator', 'SimpleHttpOperator'] 