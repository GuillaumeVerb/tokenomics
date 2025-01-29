"""Type stubs for airflow.providers.http.operators.http."""
from typing import Any, Dict, Optional, Union

from airflow.models import BaseOperator

class SimpleHttpOperator(BaseOperator):
    def __init__(
        self,
        *,
        endpoint: str,
        method: str = "POST",
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, Any]] = None,
        response_filter: Optional[Any] = None,
        http_conn_id: str = "http_default",
        task_id: str,
        dag: Optional[Any] = None,
        **kwargs: Any
    ) -> None: ... 