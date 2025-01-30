"""Type stubs for airflow.providers.http.operators.http."""
from typing import Any, Callable, Dict, Optional, Union

from ....models import BaseOperator, DAG

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