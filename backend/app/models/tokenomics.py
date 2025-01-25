from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class InflationSimulationRequest(BaseModel):
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    inflation_rate: Decimal = Field(..., ge=0, le=100, description="Annual inflation rate (percentage)")
    duration_in_years: int = Field(..., gt=0, le=100, description="Duration of simulation in years")
    
    @validator('inflation_rate')
    def validate_inflation_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Inflation rate must be between 0 and 100')
        return v

class SupplyPoint(BaseModel):
    year: int = Field(..., description="Year of simulation (0 = initial)")
    supply: Decimal = Field(..., description="Token supply at given year")

class InflationSimulationResponse(BaseModel):
    simulation_data: List[SupplyPoint]
    total_supply_increase: Decimal
    total_supply_increase_percentage: Decimal

class BurnEvent(BaseModel):
    month: int = Field(..., ge=0, description="Month when burn occurs")
    amount: Decimal = Field(..., gt=0, description="Amount of tokens to burn")

class BurnSimulationRequest(BaseModel):
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    duration_in_months: int = Field(..., gt=0, le=120, description="Duration in months")
    burn_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Monthly burn rate (percentage)")
    burn_events: Optional[List[BurnEvent]] = Field(None, description="List of specific burn events")

    @validator('burn_rate', 'burn_events')
    def validate_burn_parameters(cls, v, values):
        if 'burn_rate' not in values and 'burn_events' not in values:
            raise ValueError('Either burn_rate or burn_events must be specified')
        return v

class VestingPeriod(BaseModel):
    start_month: int = Field(..., ge=0, description="Start month of vesting period")
    duration_months: int = Field(..., gt=0, description="Duration of vesting in months")
    tokens_amount: Decimal = Field(..., gt=0, description="Amount of tokens to vest")
    cliff_months: int = Field(0, ge=0, description="Cliff period in months")

class VestingSimulationRequest(BaseModel):
    total_supply: Decimal = Field(..., gt=0, description="Total token supply")
    duration_in_months: int = Field(..., gt=0, le=120, description="Duration in months")
    vesting_periods: List[VestingPeriod] = Field(..., min_items=1, description="List of vesting periods")

class StakingSimulationRequest(BaseModel):
    total_supply: Decimal = Field(..., gt=0, description="Total token supply")
    duration_in_months: int = Field(..., gt=0, le=120, description="Duration in months")
    staking_rate: Decimal = Field(..., ge=0, le=100, description="Expected staking participation rate (%)")
    staking_reward_rate: Decimal = Field(..., ge=0, le=1000, description="Annual staking reward rate (%)")
    lock_period: int = Field(..., ge=0, description="Lock period in months")

class TokenPoint(BaseModel):
    month: int = Field(..., description="Month of simulation")
    circulating_supply: Decimal = Field(..., description="Circulating supply")
    locked_supply: Optional[Decimal] = Field(None, description="Locked supply (staking/vesting)")
    burned_supply: Optional[Decimal] = Field(None, description="Cumulative burned supply")
    staked_supply: Optional[Decimal] = Field(None, description="Currently staked supply")
    rewards_distributed: Optional[Decimal] = Field(None, description="Cumulative rewards distributed")

class SimulationResponse(BaseModel):
    simulation_data: List[TokenPoint]
    total_burned: Optional[Decimal] = Field(None, description="Total amount burned")
    total_vested: Optional[Decimal] = Field(None, description="Total amount vested")
    total_staked: Optional[Decimal] = Field(None, description="Final staked amount")
    total_rewards: Optional[Decimal] = Field(None, description="Total rewards distributed") 