from pydantic import Field, field_validator, model_validator
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime
from .base import BaseTokenomicsModel

class InflationConfig(BaseTokenomicsModel):
    type: Literal["constant", "dynamic", "halving"] = Field(..., description="Type of inflation")
    initial_rate: Decimal = Field(..., description="Initial inflation rate (%)", ge=0, le=100)
    min_rate: Optional[Decimal] = Field(None, description="Minimum inflation rate for dynamic type (%)", ge=0, le=100)
    decay_rate: Optional[Decimal] = Field(None, description="Decay rate for dynamic type (%)", ge=0, le=100)
    halving_period: Optional[int] = Field(None, description="Period in months for halving type", gt=0)

    @model_validator(mode='after')
    def validate_config(self) -> 'InflationConfig':
        if self.type == "dynamic" and (self.min_rate is None or self.decay_rate is None):
            raise ValueError("Dynamic inflation requires min_rate and decay_rate")
        if self.type == "halving" and self.halving_period is None:
            raise ValueError("Halving inflation requires halving_period")
        return self

class BurnEvent(BaseTokenomicsModel):
    """A token burn event at a specific month."""
    month: int = Field(..., ge=1, description="Month when the burn occurs")
    amount: Decimal = Field(..., gt=0, description="Amount of tokens to burn")

class VestingPeriod(BaseTokenomicsModel):
    start_month: int = Field(..., ge=0, description="Start month of vesting period")
    duration_months: int = Field(..., gt=0, description="Duration of vesting in months")
    tokens_amount: Decimal = Field(..., gt=0, description="Amount of tokens to vest")
    cliff_months: int = Field(0, ge=0, description="Cliff period in months")

class ScenarioRequest(BaseTokenomicsModel):
    initial_supply: Decimal = Field(..., description="Initial token supply", gt=0)
    duration: int = Field(..., description="Duration in months", ge=1, le=30)
    time_step: str = Field("monthly", description="Time step for simulation (monthly/yearly)")
    inflation_config: Optional[InflationConfig] = Field(None, description="Inflation configuration")
    inflation_rate: Optional[Decimal] = Field(None, description="Annual inflation rate (%)", ge=0, le=100)
    burn_rate: Optional[Decimal] = Field(None, description="Monthly burn rate (%)", ge=0, le=100)
    burn_events: Optional[List[BurnEvent]] = Field(None, description="List of burn events")
    vesting_periods: Optional[List[VestingPeriod]] = Field(None, description="List of vesting periods")
    staking_rate: Optional[Decimal] = Field(None, description="Expected staking participation rate (%)", ge=0, le=100)
    staking_reward_rate: Optional[Decimal] = Field(None, description="Annual staking reward rate (%)", ge=0, le=1000)
    staking_lock_period: Optional[int] = Field(None, description="Staking lock period in months", ge=0)

class InflationSimulationRequest(BaseTokenomicsModel):
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    inflation_rate: Decimal = Field(..., ge=0, le=100, description="Annual inflation rate (percentage)")
    duration_in_years: int = Field(..., gt=0, le=100, description="Duration of simulation in years")
    
    @field_validator('inflation_rate')
    @classmethod
    def validate_inflation_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Inflation rate must be between 0 and 100')
        return v

class SupplyPoint(BaseTokenomicsModel):
    year: int = Field(..., description="Year of simulation (0 = initial)")
    supply: Decimal = Field(..., description="Token supply at given year")

class InflationSimulationResponse(BaseTokenomicsModel):
    simulation_data: List[SupplyPoint]
    total_supply_increase: Decimal
    total_supply_increase_percentage: Decimal

class BurnSimulationRequest(BaseTokenomicsModel):
    """Request model for token burn simulation."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    duration: int = Field(..., ge=1, le=30, description="Duration in months")
    burn_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Monthly burn rate as a percentage (0-100)")
    burn_events: Optional[List[BurnEvent]] = Field(None, description="List of specific burn events")

    @model_validator(mode='after')
    def validate_burn_config(self) -> 'BurnSimulationRequest':
        """Validate that either burn_rate or burn_events is specified, but not both."""
        if self.burn_rate is not None and self.burn_events is not None:
            raise ValueError("Must specify either burn_rate or burn_events, but not both")
        if self.burn_rate is None and self.burn_events is None:
            raise ValueError("Must specify either burn_rate or burn_events")
        return self

class VestingSimulationRequest(BaseTokenomicsModel):
    total_supply: Decimal = Field(..., gt=0, description="Total token supply")
    duration: int = Field(..., ge=1, le=30, description="Duration in months")
    vesting_periods: List[VestingPeriod] = Field(..., min_items=1, description="List of vesting periods")

class StakingSimulationRequest(BaseTokenomicsModel):
    total_supply: Decimal = Field(..., gt=0, description="Total token supply")
    duration: int = Field(..., ge=1, le=30, description="Duration in months")
    staking_rate: Decimal = Field(..., ge=0, le=100, description="Expected staking participation rate (%)")
    staking_reward_rate: Decimal = Field(..., ge=0, le=1000, description="Annual staking reward rate (%)")
    lock_period: int = Field(..., ge=0, description="Lock period in months")

class TokenPoint(BaseTokenomicsModel):
    month: int = Field(..., description="Month of simulation")
    circulating_supply: Decimal = Field(..., description="Circulating supply")
    locked_supply: Optional[Decimal] = Field(None, description="Locked supply (staking/vesting)")
    burned_supply: Optional[Decimal] = Field(None, description="Cumulative burned supply")
    staked_supply: Optional[Decimal] = Field(None, description="Currently staked supply")
    rewards_distributed: Optional[Decimal] = Field(None, description="Cumulative rewards distributed")

class SimulationResponse(BaseTokenomicsModel):
    simulation_data: List[TokenPoint]
    total_burned: Optional[Decimal] = Field(None, description="Total amount burned")
    total_vested: Optional[Decimal] = Field(None, description="Total amount vested")
    total_staked: Optional[Decimal] = Field(None, description="Final staked amount")
    total_rewards: Optional[Decimal] = Field(None, description="Total rewards distributed") 