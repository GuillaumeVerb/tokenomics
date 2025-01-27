from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict

def custom_json_encoder(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

class BaseTokenomicsModel(BaseModel):
    """Base model for all tokenomics models with Decimal serialization support."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={Decimal: str},
        from_attributes=True,
        json_schema_extra={"definitions": {}}
    )

    def model_dump_json(self, **kwargs):
        kwargs.setdefault("encoder", custom_json_encoder)
        return super().model_dump_json(**kwargs) 