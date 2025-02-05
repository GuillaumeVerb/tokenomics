from decimal import Decimal
from typing import List, Optional, Literal
from pydantic import Field, field_validator, model_validator, ConfigDict
from datetime import datetime
from .base import BaseTokenomicsModel
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

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
    start_period: int = Field(default=..., ge=0, description="Start month of vesting period")
    duration: int = Field(default=..., gt=0, description="Duration of vesting in months")
    amount: Decimal = Field(default=..., gt=0, description="Amount of tokens to vest")
    cliff_duration: int = Field(default=0, ge=0, description="Cliff period in months")
    release_type: Literal["linear"] = Field(default="linear", description="Type of vesting release")

class BurnConfig(BaseTokenomicsModel):
    """Configuration for token burning."""
    type: Literal["continuous"] = Field(default=..., description="Type of burn mechanism")
    rate: Decimal = Field(default=..., description="Monthly burn rate (%)", ge=0, le=100)

class VestingConfig(BaseTokenomicsModel):
    """Configuration for token vesting."""
    periods: List[VestingPeriod] = Field(default=..., min_items=1, description="List of vesting periods")

class StakingConfig(BaseTokenomicsModel):
    """Configuration for token staking."""
    enabled: bool = Field(default=True, description="Whether staking is enabled")
    target_rate: Decimal = Field(default=..., description="Target staking participation rate (%)", ge=0, le=100)
    reward_rate: Decimal = Field(default=..., description="Annual staking reward rate (%)", ge=0, le=1000)
    lock_duration: int = Field(default=..., description="Lock period in months", ge=0)

class ScenarioRequest(BaseTokenomicsModel):
    """Base request model for tokenomics scenarios."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    time_step: str = Field(..., pattern="^(monthly|yearly)$", description="Time step for simulation")
    duration: int = Field(..., gt=0, le=360, description="Duration of simulation")
    inflation_config: Optional[InflationConfig] = Field(default=None, description="Inflation configuration")
    burn_config: Optional[BurnConfig] = Field(default=None, description="Burn configuration")
    vesting_config: Optional[VestingConfig] = Field(default=None, description="Vesting configuration")
    staking_config: Optional[StakingConfig] = Field(default=None, description="Staking configuration")

    @property
    def duration_in_months(self) -> int:
        """Get duration in months based on time step."""
        return self.duration * 12 if self.time_step == "yearly" else self.duration

    @model_validator(mode='after')
    def validate_configs(self) -> 'ScenarioRequest':
        """Ensure at least one configuration is provided."""
        if not any([
            self.inflation_config,
            self.burn_config,
            self.vesting_config,
            self.staking_config
        ]):
            raise ValueError("At least one configuration must be provided")
        return self

class NamedScenarioRequest(ScenarioRequest):
    """ScenarioRequest with a name for comparison."""
    name: str = Field(..., min_length=1, max_length=50, description="Name of the scenario")

class TokenPoint(BaseTokenomicsModel):
    month: int = Field(default=..., ge=0, description="Month of simulation")
    circulating_supply: Decimal = Field(default=..., ge=0, description="Circulating supply")
    locked_supply: Optional[Decimal] = Field(default=None, description="Locked supply (staking/vesting)", ge=0)
    burned_supply: Optional[Decimal] = Field(default=None, description="Cumulative burned supply", ge=0)
    staked_supply: Optional[Decimal] = Field(default=None, description="Currently staked supply", ge=0)
    rewards_distributed: Optional[Decimal] = Field(default=None, description="Cumulative rewards distributed", ge=0)
    total_supply: Optional[Decimal] = Field(default=None, description="Total token supply")

    class Config:
        json_encoders = {Decimal: str}

class PeriodMetrics(BaseTokenomicsModel):
    """Metrics for a single period in the simulation."""
    period: int = Field(default=..., ge=0, description="Period number")
    total_supply: Decimal = Field(default=..., ge=0, description="Total token supply")
    circulating_supply: Decimal = Field(default=..., ge=0, description="Circulating supply")
    minted_amount: Decimal = Field(default=0, ge=0, description="Amount minted in this period")
    burned_amount: Decimal = Field(default=0, ge=0, description="Amount burned in this period")
    vested_amount: Decimal = Field(default=0, ge=0, description="Amount vested in this period")
    staked_amount: Decimal = Field(default=0, ge=0, description="Amount staked in this period")
    staking_rewards: Decimal = Field(default=0, ge=0, description="Staking rewards distributed in this period")
    locked_amount: Decimal = Field(default=0, ge=0, description="Total amount locked (staking + vesting)")

    class Config:
        json_encoders = {Decimal: str}

class SimulationResponse(BaseTokenomicsModel):
    simulation_data: List[TokenPoint] = Field(default=...)
    total_burned: Optional[Decimal] = Field(default=None, description="Total amount burned", ge=0)
    total_vested: Optional[Decimal] = Field(default=None, description="Total amount vested", ge=0)
    total_staked: Optional[Decimal] = Field(default=None, description="Final staked amount", ge=0)
    total_rewards: Optional[Decimal] = Field(default=None, description="Total rewards distributed", ge=0)

class ComparisonRequest(BaseTokenomicsModel):
    scenarios: List[NamedScenarioRequest] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of scenarios to compare"
    )
    return_combined_graph: bool = Field(default=False)
    metrics_to_graph: Optional[List[str]] = Field(default=None)

    @field_validator('metrics_to_graph')
    def validate_metrics(cls, v):
        if v is None:
            return v
        valid_metrics = {'total_supply', 'circulating_supply', 'locked_supply', 'staked_supply'}
        invalid_metrics = set(v) - valid_metrics
        if invalid_metrics:
            raise ValueError(f"Invalid metrics: {invalid_metrics}")
        return v

class ComparisonSummary(BaseTokenomicsModel):
    """Summary of scenario comparison."""
    supply_range: dict = Field(..., description="Range of final supplies")
    minted_range: dict = Field(..., description="Range of total minted amounts")
    burned_range: dict = Field(..., description="Range of total burned amounts")
    staked_range: dict = Field(..., description="Range of staked amounts")

class ConstantInflationRequest(BaseTokenomicsModel):
    """Request model for constant inflation simulation."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    inflation_rate: Decimal = Field(..., ge=0, le=100, description="Annual inflation rate (%)")
    duration_in_years: int = Field(..., gt=0, le=30, description="Duration in years")

class SupplyPoint(BaseTokenomicsModel):
    year: int = Field(default=..., ge=0, description="Year of simulation (0 = initial)")
    supply: Decimal = Field(default=..., gt=0, description="Token supply at given year")

    class Config:
        json_encoders = {Decimal: str}

class InflationSimulationResponse(BaseTokenomicsModel):
    simulation_data: List[SupplyPoint] = Field(default=...)
    total_supply_increase: Decimal = Field(default=..., gt=0)
    total_supply_increase_percentage: Decimal = Field(default=..., ge=0)

class BurnRequest(BaseTokenomicsModel):
    """Request model for token burn simulation."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    duration_in_months: int = Field(..., ge=1, le=360, description="Duration in months")
    burn_rate: Optional[Decimal] = Field(default=None, ge=0, le=100, description="Monthly burn rate (%)")
    burn_events: Optional[List[BurnEvent]] = Field(default=None, description="List of burn events")

    @model_validator(mode='after')
    def validate_burn_config(self) -> 'BurnRequest':
        """Validate that either burn_rate or burn_events is specified, but not both."""
        if self.burn_rate is not None and self.burn_events is not None:
            raise ValueError("Must specify either burn_rate or burn_events, but not both")
        if self.burn_rate is None and self.burn_events is None:
            raise ValueError("Must specify either burn_rate or burn_events")
        return self

class VestingRequest(BaseTokenomicsModel):
    """Request model for token vesting simulation."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    duration_in_months: int = Field(..., ge=1, le=360, description="Duration in months")
    vesting_config: VestingConfig = Field(..., description="Vesting configuration")

class StakingRequest(BaseTokenomicsModel):
    """Request model for token staking simulation."""
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    duration_in_months: int = Field(..., ge=1, le=360, description="Duration in months")
    staking_config: StakingConfig = Field(..., description="Staking configuration")

class ScenarioSummary(BaseTokenomicsModel):
    """Summary of a tokenomics scenario simulation."""
    final_supply: Decimal = Field(..., description="Final token supply")
    total_minted: Decimal = Field(..., description="Total tokens minted")
    total_burned: Decimal = Field(..., description="Total tokens burned")
    total_vested: Decimal = Field(..., description="Total tokens vested")
    total_staking_rewards: Decimal = Field(..., description="Total staking rewards distributed")
    current_staked: Decimal = Field(..., description="Current staked supply")
    current_locked: Decimal = Field(..., description="Current locked supply")
    supply_change_percentage: Decimal = Field(..., description="Percentage change in supply")

class ScenarioResponse(BaseTokenomicsModel):
    """Response model for scenario simulation."""
    timeline: List[PeriodMetrics] = Field(..., description="Timeline of token metrics")
    summary: ScenarioSummary = Field(..., description="Summary of simulation results")
    simulation_data: Optional[List[TokenPoint]] = Field(None, description="Raw simulation data points")

    model_config = ConfigDict(
        json_encoders={Decimal: str},
        validate_assignment=True,
        extra='forbid'
    ) 