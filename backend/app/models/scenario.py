from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime

class InflationConfig(BaseModel):
    type: Literal["constant", "dynamic", "halving"] = Field(
        ..., 
        description="Type of inflation mechanism"
    )
    initial_rate: Decimal = Field(
        ..., 
        gt=0, 
        le=100, 
        description="Initial annual inflation rate (%)"
    )
    halving_period: Optional[int] = Field(
        None,
        gt=0,
        description="Period (in years) after which inflation rate is halved"
    )
    min_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Minimum inflation rate for dynamic inflation"
    )
    decay_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Annual decay rate for dynamic inflation"
    )

class BurnEvent(BaseModel):
    period: int = Field(..., ge=0, description="Period when burn occurs")
    amount: Decimal = Field(..., gt=0, description="Amount to burn")
    
class BurnConfig(BaseModel):
    type: Literal["continuous", "event-based"] = Field(
        ..., 
        description="Type of burn mechanism"
    )
    rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Continuous burn rate (%)"
    )
    events: Optional[List[BurnEvent]] = Field(
        None,
        description="List of specific burn events"
    )

    @validator('rate', 'events')
    def validate_burn_config(cls, v, values):
        if values.get('type') == 'continuous' and not v and 'rate' in values:
            raise ValueError('Continuous burn requires a rate')
        if values.get('type') == 'event-based' and not v and 'events' in values:
            raise ValueError('Event-based burn requires events list')
        return v

class VestingPeriod(BaseModel):
    start_period: int = Field(..., ge=0, description="Start period of vesting")
    duration: int = Field(..., gt=0, description="Duration of vesting")
    amount: Decimal = Field(..., gt=0, description="Amount of tokens to vest")
    cliff_duration: int = Field(0, ge=0, description="Cliff duration")
    release_type: Literal["linear", "exponential"] = Field(
        "linear",
        description="Type of token release schedule"
    )

class VestingConfig(BaseModel):
    periods: List[VestingPeriod] = Field(
        ...,
        min_items=1,
        description="List of vesting periods"
    )

class StakingConfig(BaseModel):
    enabled: bool = Field(..., description="Whether staking is enabled")
    target_rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        description="Target staking participation rate (%)"
    )
    reward_rate: Decimal = Field(
        ...,
        ge=0,
        le=1000,
        description="Annual staking reward rate (%)"
    )
    lock_duration: int = Field(
        ...,
        ge=0,
        description="Lock duration for staked tokens"
    )

class ScenarioRequest(BaseModel):
    initial_supply: Decimal = Field(
        ...,
        gt=0,
        description="Initial token supply"
    )
    time_step: Literal["monthly", "yearly"] = Field(
        ...,
        description="Time step for simulation"
    )
    duration: int = Field(
        ...,
        gt=0,
        le=360 if time_step == "monthly" else 30,
        description="Duration of simulation in periods"
    )
    inflation_config: Optional[InflationConfig] = Field(
        None,
        description="Inflation mechanism configuration"
    )
    burn_config: Optional[BurnConfig] = Field(
        None,
        description="Burn mechanism configuration"
    )
    vesting_config: Optional[VestingConfig] = Field(
        None,
        description="Vesting schedule configuration"
    )
    staking_config: Optional[StakingConfig] = Field(
        None,
        description="Staking mechanism configuration"
    )

class PeriodMetrics(BaseModel):
    period: int = Field(..., description="Period number")
    total_supply: Decimal = Field(..., description="Total token supply")
    circulating_supply: Decimal = Field(..., description="Circulating supply")
    minted_amount: Decimal = Field(..., description="Tokens minted this period")
    burned_amount: Decimal = Field(..., description="Tokens burned this period")
    vested_amount: Decimal = Field(..., description="Tokens vested this period")
    staked_amount: Decimal = Field(..., description="Tokens staked")
    staking_rewards: Decimal = Field(..., description="Staking rewards distributed")
    locked_amount: Decimal = Field(..., description="Tokens locked (vesting + staking)")

class ScenarioSummary(BaseModel):
    final_supply: Decimal = Field(..., description="Final token supply")
    total_minted: Decimal = Field(..., description="Total tokens minted")
    total_burned: Decimal = Field(..., description="Total tokens burned")
    total_vested: Decimal = Field(..., description="Total tokens vested")
    total_staking_rewards: Decimal = Field(..., description="Total staking rewards")
    current_staked: Decimal = Field(..., description="Currently staked tokens")
    current_locked: Decimal = Field(..., description="Currently locked tokens")
    supply_change_percentage: Decimal = Field(..., description="Total supply change (%)")

class ScenarioResponse(BaseModel):
    timeline: List[PeriodMetrics] = Field(..., description="Period by period metrics")
    summary: ScenarioSummary = Field(..., description="Scenario summary metrics") 