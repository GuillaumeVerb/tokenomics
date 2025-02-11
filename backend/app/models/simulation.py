from decimal import Decimal
from typing import Optional

from pydantic import Field, BaseModel

from .base import BaseTokenomicsModel


class SimulationParams(BaseModel):
    """Parameters for tokenomics simulation."""
    initial_supply: float = Field(..., description="Initial token supply", gt=0)
    initial_price: float = Field(..., description="Initial token price", gt=0)
    initial_liquidity: float = Field(..., description="Initial liquidity ratio", gt=0, le=1)
    simulation_months: int = Field(..., description="Duration of simulation in months", gt=0)
    monthly_inflation: float = Field(..., description="Monthly inflation rate", ge=0, le=1)
    vesting_period: int = Field(..., description="Vesting period in months", ge=0)


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
