from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict
import json

def custom_json_encoder(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

class BaseTokenomicsModel(BaseModel):
    """Base model for all tokenomics models."""
    model_config = ConfigDict(
        json_encoders={Decimal: str},
        validate_assignment=True,
        extra='forbid'
    )

    def model_dump(self, *args, **kwargs):
        """Override model_dump to handle Decimal serialization."""
        data = super().model_dump(*args, **kwargs)
        return self._convert_decimals(data)

    def _convert_decimals(self, data):
        """Convert Decimal objects to strings in nested structures."""
        if isinstance(data, dict):
            return {k: self._convert_decimals(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_decimals(v) for v in data]
        elif isinstance(data, Decimal):
            return str(data)
        return data

    def model_dump_json(self, **kwargs):
        """Override model_dump_json to handle Decimal serialization."""
        data = self.model_dump()
        return json.dumps(data, default=str) 