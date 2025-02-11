from decimal import Decimal
from typing import Optional

from pydantic import Field

from .base import BaseTokenomicsModel


class TokenPoint(BaseTokenomicsModel):
    """A point in time during token simulation."""

    month: int = Field(..., description="Month number", ge=0)
    total_supply: Optional[Decimal] = Field(None, description="Total token supply")
    circulating_supply: Optional[Decimal] = Field(
        None, description="Circulating token supply"
    )
    locked_supply: Optional[Decimal] = Field(None, description="Locked token supply")
    burned_supply: Optional[Decimal] = Field(None, description="Total burned tokens")
    staked_supply: Optional[Decimal] = Field(None, description="Total staked tokens")
    rewards_distributed: Optional[Decimal] = Field(
        None, description="Total rewards distributed"
    )
