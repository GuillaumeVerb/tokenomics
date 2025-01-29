"""Type stubs for airflow."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from airflow.models import BaseOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

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