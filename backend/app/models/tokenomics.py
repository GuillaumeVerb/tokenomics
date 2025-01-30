from pydantic import Field, field_validator, model_validator
from typing import List, Optional, Literal, Any
from decimal import Decimal
from datetime import datetime
from .base import BaseTokenomicsModel

class InflationConfig(BaseTokenomicsModel):
    type: Literal["constant", "dynamic", "halving"] = Field(default=..., description="Type of inflation")
    initial_rate: Decimal = Field(default=..., description="Initial inflation rate (%)", ge=0, le=100)
    min_rate: Optional[Decimal] = Field(default=None, description="Minimum inflation rate for dynamic type (%)", ge=0, le=100)
    decay_rate: Optional[Decimal] = Field(default=None, description="Decay rate for dynamic type (%)", ge=0, le=100)
    halving_period: Optional[int] = Field(default=None, description="Period in months for halving type", gt=0)

    @model_validator(mode='after')
    def validate_config(self) -> 'InflationConfig':
        if self.type == "dynamic" and (self.min_rate is None or self.decay_rate is None):
            raise ValueError("Dynamic inflation requires min_rate and decay_rate")
        if self.type == "halving" and self.halving_period is None:
            raise ValueError("Halving inflation requires halving_period")
        return self

class BurnEvent(BaseTokenomicsModel):
    """A token burn event at a specific month."""
    month: int = Field(default=..., ge=1, description="Month when the burn occurs")
    amount: Decimal = Field(default=..., gt=0, description="Amount of tokens to burn")

class VestingPeriod(BaseTokenomicsModel):
    start_month: int = Field(default=..., ge=0, description="Start month of vesting period")
    duration_months: int = Field(default=..., gt=0, description="Duration of vesting in months")
    tokens_amount: Decimal = Field(default=..., gt=0, description="Amount of tokens to vest")
    cliff_months: int = Field(default=0, ge=0, description="Cliff period in months")

class ScenarioRequest(BaseTokenomicsModel):
    initial_supply: Decimal = Field(default=..., gt=0, description="Initial token supply")
    duration: int = Field(default=..., ge=1, le=30, description="Duration in months")
    time_step: str = Field(default="monthly", description="Time step for simulation (monthly/yearly)")
    inflation_config: Optional[InflationConfig] = Field(default=None, description="Inflation configuration")
    inflation_rate: Optional[Decimal] = Field(default=None, description="Annual inflation rate (%)", ge=0, le=100)
    burn_rate: Optional[Decimal] = Field(default=None, description="Monthly burn rate (%)", ge=0, le=100)
    burn_events: Optional[List[BurnEvent]] = Field(default=None, description="List of burn events")
    vesting_periods: Optional[List[VestingPeriod]] = Field(default=None, description="List of vesting periods")
    staking_rate: Optional[Decimal] = Field(default=None, description="Expected staking participation rate (%)", ge=0, le=100)
    staking_reward_rate: Optional[Decimal] = Field(default=None, description="Annual staking reward rate (%)", ge=0, le=1000)
    staking_lock_period: Optional[int] = Field(default=None, description="Staking lock period in months", ge=0)

class InflationSimulationRequest(BaseTokenomicsModel):
    initial_supply: Decimal = Field(default=..., gt=0, description="Initial token supply")
    inflation_rate: Decimal = Field(default=..., ge=0, le=100, description="Annual inflation rate (percentage)")
    duration_in_years: int = Field(default=..., gt=0, le=100, description="Duration of simulation in years")
    
    @field_validator('inflation_rate')
    @classmethod
    def validate_inflation_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Inflation rate must be between 0 and 100')
        return v

class SupplyPoint(BaseTokenomicsModel):
    year: int = Field(default=..., ge=0, description="Year of simulation (0 = initial)")
    supply: Decimal = Field(default=..., gt=0, description="Token supply at given year")

class InflationSimulationResponse(BaseTokenomicsModel):
    simulation_data: List[SupplyPoint] = Field(default=...)
    total_supply_increase: Decimal = Field(default=..., gt=0)
    total_supply_increase_percentage: Decimal = Field(default=..., ge=0, le=100)

class BurnSimulationRequest(BaseTokenomicsModel):
    """Request model for token burn simulation."""
    initial_supply: Decimal = Field(default=..., gt=0, description="Initial token supply")
    duration: int = Field(default=..., ge=1, le=30, description="Duration in months")
    burn_rate: Optional[Decimal] = Field(default=None, description="Monthly burn rate as a percentage (0-100)", ge=0, le=100)
    burn_events: Optional[List[BurnEvent]] = Field(default=None, description="List of specific burn events")

    @model_validator(mode='after')
    def validate_burn_config(self) -> 'BurnSimulationRequest':
        """Validate that either burn_rate or burn_events is specified, but not both."""
        if self.burn_rate is not None and self.burn_events is not None:
            raise ValueError("Must specify either burn_rate or burn_events, but not both")
        if self.burn_rate is None and self.burn_events is None:
            raise ValueError("Must specify either burn_rate or burn_events")
        return self

class VestingSimulationRequest(BaseTokenomicsModel):
    total_supply: Decimal = Field(default=..., gt=0, description="Total token supply")
    duration: int = Field(default=..., ge=1, le=30, description="Duration in months")
    vesting_periods: List[VestingPeriod] = Field(default=..., min_items=1, description="List of vesting periods")

class StakingSimulationRequest(BaseTokenomicsModel):
    total_supply: Decimal = Field(default=..., gt=0, description="Total token supply")
    duration: int = Field(default=..., ge=1, le=30, description="Duration in months")
    staking_rate: Decimal = Field(default=..., ge=0, le=100, description="Expected staking participation rate (%)")
    staking_reward_rate: Decimal = Field(default=..., ge=0, le=1000, description="Annual staking reward rate (%)")
    lock_period: int = Field(default=..., ge=0, description="Lock period in months")

class TokenPoint(BaseTokenomicsModel):
    month: int = Field(default=..., ge=0, description="Month of simulation")
    circulating_supply: Decimal = Field(default=..., gt=0, description="Circulating supply")
    locked_supply: Optional[Decimal] = Field(default=None, description="Locked supply (staking/vesting)", ge=0)
    burned_supply: Optional[Decimal] = Field(default=None, description="Cumulative burned supply", ge=0)
    staked_supply: Optional[Decimal] = Field(default=None, description="Currently staked supply", ge=0)
    rewards_distributed: Optional[Decimal] = Field(default=None, description="Cumulative rewards distributed", ge=0)

class SimulationResponse(BaseTokenomicsModel):
    simulation_data: List[TokenPoint] = Field(default=...)
    total_burned: Optional[Decimal] = Field(default=None, description="Total amount burned", ge=0)
    total_vested: Optional[Decimal] = Field(default=None, description="Total amount vested", ge=0)
    total_staked: Optional[Decimal] = Field(default=None, description="Final staked amount", ge=0)
    total_rewards: Optional[Decimal] = Field(default=None, description="Total rewards distributed", ge=0) 