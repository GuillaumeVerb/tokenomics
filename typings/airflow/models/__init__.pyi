"""Type stubs for airflow.models."""
from typing import Any, Dict, Optional

class BaseOperator:
    def __init__(
        self,
        task_id: str,
        dag: Optional[Any] = None,
        **kwargs: Any
    ) -> None: ... 