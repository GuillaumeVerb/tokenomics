from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, TypeVar, Union, cast

import plotly.graph_objects as go
from app.models.tokenomics import (
    BurnSimulationRequest,
    InflationSimulationRequest,
    InflationSimulationResponse,
    SimulationResponse,
    StakingSimulationRequest,
    VestingSimulationRequest,
)
from app.services.simulation_service import (
    calculate_constant_inflation,
    calculate_supply_increase,
)
from app.services.token_simulation_service import (
    simulate_burn,
    simulate_staking,
    simulate_vesting,
)
from fastapi import APIRouter, HTTPException
from plotly.subplots import make_subplots

from ..models.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummary,
    PlotlyGraph,
    ScenarioComparison,
)
from ..models.scenario import (
    BurnConfig,
    InflationConfig,
    PeriodMetrics,
    ScenarioRequest,
    ScenarioResponse,
    ScenarioSummary,
    StakingConfig,
    VestingConfig,
)

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post(
    "/constant_inflation",
    response_model=InflationSimulationResponse,
    summary="Simulate constant inflation",
    description="""
    Simulates token supply evolution with a constant inflation rate over a specified period.
    
    The simulation:
    - Starts with the initial supply
    - Applies the same inflation rate each year
    - Returns supply values for each year
    
    Example:
    ```
    {
        "initial_supply": 1000000,
        "inflation_rate": 5,
        "duration_in_years": 10
    }
    ```
    """
)
async def simulate_constant_inflation(
    request: InflationSimulationRequest
) -> InflationSimulationResponse:
    try:
        # Calculate supply evolution
        simulation_data = calculate_constant_inflation(
            request.initial_supply,
            request.inflation_rate,
            request.duration_in_years
        )
        
        # Calculate total increases
        total_increase, percentage_increase = calculate_supply_increase(simulation_data)
        
        return InflationSimulationResponse(
            simulation_data=simulation_data,
            total_supply_increase=total_increase,
            total_supply_increase_percentage=percentage_increase
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in simulation calculation: {str(e)}"
        )

@router.post(
    "/burn",
    response_model=SimulationResponse,
    summary="Simulate token burning",
    description="""
    Simulates token burning through either:
    - A continuous burn rate applied monthly
    - Specific burn events at defined months
    
    Example:
    ```json
    {
        "initial_supply": 1000000,
        "duration_in_months": 24,
        "burn_rate": 1.5,
        "burn_events": [
            {"month": 6, "amount": 100000},
            {"month": 12, "amount": 50000}
        ]
    }
    ```
    """
)
async def simulate_token_burn(request: BurnSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_burn(request)
        total_burned = simulation_data[-1].burned_supply if simulation_data else None
        return SimulationResponse(
            simulation_data=simulation_data,
            total_burned=total_burned
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/vesting",
    response_model=SimulationResponse,
    summary="Simulate token vesting",
    description="""
    Simulates token vesting schedules with:
    - Multiple vesting periods
    - Cliff periods
    - Linear or custom release schedules
    
    Example:
    ```json
    {
        "total_supply": 1000000,
        "duration_in_months": 36,
        "vesting_periods": [
            {
                "start_month": 0,
                "duration_months": 24,
                "tokens_amount": 400000,
                "cliff_months": 6
            },
            {
                "start_month": 12,
                "duration_months": 12,
                "tokens_amount": 600000,
                "cliff_months": 0
            }
        ]
    }
    ```
    """
)
async def simulate_token_vesting(request: VestingSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_vesting(request)
        total_vested = simulation_data[-1].circulating_supply if simulation_data else None
        return SimulationResponse(
            simulation_data=simulation_data,
            total_vested=total_vested
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/staking",
    response_model=SimulationResponse,
    summary="Simulate token staking",
    description="""
    Simulates token staking mechanism with:
    - Expected staking participation rate
    - Staking rewards
    - Lock periods
    
    Example:
    ```json
    {
        "total_supply": 1000000,
        "duration_in_months": 12,
        "staking_rate": 60,
        "staking_reward_rate": 12.5,
        "lock_period": 3
    }
    ```
    """
)
async def simulate_token_staking(request: StakingSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_staking(request)
        final_data = simulation_data[-1]
        return SimulationResponse(
            simulation_data=simulation_data,
            total_staked=final_data.staked_supply,
            total_rewards=final_data.rewards_distributed
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def calculate_inflation(
    current_supply: Decimal,
    config: Optional[InflationConfig],
    period: int,
    is_monthly: bool = True
) -> Decimal:
    """Calculate inflation for a given period."""
    if not config or not config.initial_rate:
        return Decimal('0')
        
    if config.type == "constant":
        rate = Decimal(str(config.initial_rate))
    elif config.type == "halving":
        halving_period = int(config.halving_period or 1)
        halvings = period // (halving_period * (12 if is_monthly else 1))
        rate = Decimal(str(config.initial_rate)) / Decimal(str(2 ** halvings))
    else:  # dynamic
        min_rate = Decimal(str(config.min_rate or 0))
        decay_rate = Decimal(str(config.decay_rate or 0))
        decay = decay_rate / Decimal(str(12 if is_monthly else 1))
        rate = max(
            min_rate,
            Decimal(str(config.initial_rate)) * ((Decimal('1') - decay/Decimal('100')) ** period)
        )
    
    # Convert annual rate to monthly if needed
    if is_monthly:
        rate = rate / Decimal('12')
    
    return current_supply * (rate / Decimal('100'))

def calculate_burn(
    current_supply: Decimal,
    config: Optional[BurnConfig],
    period: int
) -> Decimal:
    """Calculate burn amount for a given period."""
    if not config:
        return cast(Decimal, Decimal('0'))
        
    if config.type == "continuous":
        rate = Decimal(str(config.rate or 0))
        return current_supply * (rate / Decimal('100'))
    else:  # event-based
        if not config.events:
            return cast(Decimal, Decimal('0'))
        return cast(Decimal, sum(
            Decimal(str(event.amount)) for event in config.events
            if event.period == period
        ))

def calculate_vesting(
    config: Optional[VestingConfig],
    period: int
) -> Decimal:
    """Calculate vesting amount for a given period."""
    if not config or not config.periods:
        return Decimal('0')
    
    total_vested = Decimal('0')
    for vest in config.periods:
        if period < vest.start_period:
            continue
        
        periods_since_start = period - vest.start_period
        
        if periods_since_start < vest.cliff_duration:
            continue
        
        if periods_since_start >= vest.duration:
            continue
        
        if vest.release_type == "linear":
            if periods_since_start == vest.cliff_duration:
                total_vested += (
                    Decimal(str(vest.amount)) * 
                    Decimal(str(vest.cliff_duration)) / 
                    Decimal(str(vest.duration))
                )
            else:
                remaining_periods = vest.duration - vest.cliff_duration
                if remaining_periods > 0:
                    monthly_amount = (
                        Decimal(str(vest.amount)) * 
                        (Decimal('1') - Decimal(str(vest.cliff_duration)) / Decimal(str(vest.duration))) /
                        Decimal(str(remaining_periods))
                    )
                    total_vested += monthly_amount
    
    return total_vested

def calculate_staking(
    config: Optional[StakingConfig],
    current_supply: Decimal,
    current_staked: Decimal,
    period: int,
    is_monthly: bool = True
) -> tuple[Decimal, Decimal]:
    """Calculate staking changes and rewards."""
    if not config or not config.enabled:
        return Decimal('0'), Decimal('0')
    
    # Convert annual rate to monthly if needed
    reward_rate = Decimal(str(config.reward_rate or 0))
    if is_monthly:
        reward_rate = reward_rate / Decimal('12')
    
    # Calculate rewards
    rewards = current_staked * (reward_rate / Decimal('100'))
    
    # Calculate target staked amount
    target_staked = current_supply * (Decimal(str(config.target_rate or 0)) / Decimal('100'))
    
    # Adjust staking based on target
    if current_staked < target_staked:
        available_for_staking = current_supply - current_staked
        staking_increase = min(
            (target_staked - current_staked) * Decimal('0.1'),  # 10% monthly progress toward target
            available_for_staking
        )
        current_staked += staking_increase
    
    return current_staked, rewards

@router.post("/simulate/scenario", response_model=ScenarioResponse)
async def simulate_scenario(request: ScenarioRequest) -> ScenarioResponse:
    timeline: List[PeriodMetrics] = []
    
    # Initialize tracking variables
    total_supply = request.initial_supply
    total_minted = Decimal(0)
    total_burned = Decimal(0)
    total_vested = Decimal(0)
    total_staking_rewards = Decimal(0)
    
    # Initialize first period
    staked_amount, staking_rewards = calculate_staking(
        request.staking_config,
        request.initial_supply,
        Decimal(0),
        0,
        request.time_step == "monthly"
    )
    
    timeline.append(PeriodMetrics(
        period=0,
        total_supply=total_supply,
        circulating_supply=total_supply - staked_amount,
        minted_amount=Decimal(0),
        burned_amount=Decimal(0),
        vested_amount=Decimal(0),
        staked_amount=staked_amount,
        staking_rewards=staking_rewards,
        locked_amount=staked_amount
    ))
    
    # Simulate each period
    for period in range(1, request.duration + 1):
        # 1. Calculate inflation
        minted = calculate_inflation(
            total_supply,
            request.inflation_config,
            period,
            request.time_step == "monthly"
        )
        total_supply += minted
        total_minted += minted
        
        # 2. Calculate burn
        burned = calculate_burn(
            total_supply,
            request.burn_config,
            period
        )
        total_supply -= burned
        total_burned += burned
        
        # 3. Calculate vesting
        vested = calculate_vesting(
            request.vesting_config,
            period
        )
        total_vested += vested
        
        # 4. Calculate staking
        staked_amount, staking_rewards = calculate_staking(
            request.staking_config,
            total_supply - staked_amount,
            staked_amount,
            period,
            request.time_step == "monthly"
        )
        total_supply += staking_rewards
        total_minted += staking_rewards
        total_staking_rewards += staking_rewards
        
        # Record period metrics
        timeline.append(PeriodMetrics(
            period=period,
            total_supply=total_supply,
            circulating_supply=total_supply - staked_amount,
            minted_amount=minted + staking_rewards,
            burned_amount=burned,
            vested_amount=vested,
            staked_amount=staked_amount,
            staking_rewards=staking_rewards,
            locked_amount=staked_amount + (total_vested - vested)
        ))
    
    # Calculate summary
    supply_change = ((total_supply - request.initial_supply) 
                    / request.initial_supply * 100)
    
    summary = ScenarioSummary(
        final_supply=total_supply,
        total_minted=total_minted,
        total_burned=total_burned,
        total_vested=total_vested,
        total_staking_rewards=total_staking_rewards,
        current_staked=staked_amount,
        current_locked=staked_amount + total_vested,
        supply_change_percentage=supply_change
    )
    
    return ScenarioResponse(timeline=timeline, summary=summary)

def generate_comparison_graph(scenarios: List[ScenarioComparison], metrics: List[str]) -> PlotlyGraph:
    """Generate a combined Plotly graph for multiple scenarios."""
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    
    for idx, scenario in enumerate(scenarios):
        color = colors[idx % len(colors)]
        periods = [m.period for m in scenario.timeline]
        
        for metric in metrics:
            values = [getattr(m, metric) for m in scenario.timeline]
            
            # Use secondary y-axis for percentages
            use_secondary = metric.endswith('_percentage')
            
            fig.add_trace(
                go.Scatter(
                    x=periods,
                    y=values,
                    name=f"{scenario.name} - {metric}",
                    line=dict(color=color, dash='dot' if use_secondary else 'solid'),
                ),
                secondary_y=use_secondary
            )
    
    fig.update_layout(
        title="Scenario Comparison",
        xaxis_title="Period",
        yaxis_title="Token Amount",
        yaxis2_title="Percentage",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return PlotlyGraph(
        data=fig.to_dict()['data'],
        layout=fig.to_dict()['layout']
    )

def calculate_range_summary(scenarios: List[ScenarioComparison]) -> ComparisonSummary:
    """Calculate summary ranges across all scenarios."""
    def get_range(values: List[Decimal]) -> Dict[str, Decimal]:
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }
    
    return ComparisonSummary(
        supply_range=get_range([s.summary.final_supply for s in scenarios]),
        minted_range=get_range([s.summary.total_minted for s in scenarios]),
        burned_range=get_range([s.summary.total_burned for s in scenarios]),
        staked_range=get_range([s.summary.current_staked for s in scenarios]),
        supply_change_range=get_range([s.summary.supply_change_percentage for s in scenarios])
    )

@router.post(
    "/compare",
    response_model=ComparisonResponse,
    summary="Compare multiple tokenomics scenarios",
    description="""
    Simulates and compares multiple tokenomics scenarios side by side.
    
    Features:
    - Compare 2-5 scenarios with different parameters
    - Get detailed metrics for each scenario
    - Optional combined Plotly graph
    - Summary of ranges across scenarios
    
    Example:
    ```json
    {
        "scenarios": [
            {
                "name": "Conservative",
                "initial_supply": 1000000,
                "time_step": "monthly",
                "duration": 24,
                "inflation_config": {
                    "type": "dynamic",
                    "initial_rate": 5.0,
                    "min_rate": 2.0,
                    "decay_rate": 20.0
                }
            },
            {
                "name": "Aggressive",
                "initial_supply": 1000000,
                "time_step": "monthly",
                "duration": 24,
                "inflation_config": {
                    "type": "dynamic",
                    "initial_rate": 10.0,
                    "min_rate": 5.0,
                    "decay_rate": 10.0
                }
            }
        ],
        "return_combined_graph": true
    }
    ```
    """
)
async def compare_scenarios(request: ComparisonRequest) -> ComparisonResponse:
    try:
        # Simulate each scenario
        scenario_results = []
        for scenario_req in request.scenarios:
            # Convert NamedScenarioRequest to ScenarioRequest
            base_req = ScenarioRequest(
                initial_supply=scenario_req.initial_supply,
                time_step=scenario_req.time_step,
                duration=scenario_req.duration,
                inflation_config=scenario_req.inflation_config,
                burn_config=scenario_req.burn_config,
                vesting_config=scenario_req.vesting_config,
                staking_config=scenario_req.staking_config
            )
            
            # Run simulation
            result = await simulate_scenario(base_req)
            
            # Add to results
            scenario_results.append(ScenarioComparison(
                name=scenario_req.name,
                timeline=result.timeline,
                summary=result.summary
            ))
        
        # Calculate comparison summary
        comparison_summary = calculate_range_summary(scenario_results)
        
        # Generate combined graph if requested
        combined_graph = None
        if request.return_combined_graph:
            metrics = request.metrics_to_graph or ["total_supply", "circulating_supply"]
            combined_graph = generate_comparison_graph(scenario_results, metrics)
        
        return ComparisonResponse(
            scenarios=scenario_results,
            comparison_summary=comparison_summary,
            combined_graph=combined_graph
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in scenario comparison: {str(e)}"
        )

T = TypeVar('T', bound=Union[int, float, Decimal, None])

def to_decimal(value: T) -> Decimal:
    """Convert any numeric value to Decimal safely."""
    if value is None:
        return Decimal('0')
    return Decimal(str(value))

@dataclass
class MetricsSummary:
    final_supply: Decimal
    total_minted: Decimal
    total_burned: Decimal
    current_staked: Decimal
    supply_change_percentage: Decimal

    @classmethod
    def create_zero(cls) -> 'MetricsSummary':
        zero = Decimal('0')
        return cls(
            final_supply=zero,
            total_minted=zero,
            total_burned=zero,
            current_staked=zero,
            supply_change_percentage=zero
        )

    def to_dict(self) -> Dict[str, Decimal]:
        """Convert to dictionary with guaranteed Decimal values."""
        result: Dict[str, Decimal] = {
            "final_supply": cast(Decimal, to_decimal(self.final_supply)),
            "total_minted": cast(Decimal, to_decimal(self.total_minted)),
            "total_burned": cast(Decimal, to_decimal(self.total_burned)),
            "current_staked": cast(Decimal, to_decimal(self.current_staked)),
            "supply_change_percentage": cast(Decimal, to_decimal(self.supply_change_percentage))
        }
        return result

def get_metrics_summary(metrics: List[PeriodMetrics]) -> Dict[str, Decimal]:
    """Calculate summary metrics from a list of period metrics."""
    if not metrics:
        return MetricsSummary.create_zero().to_dict()
    
    last_point = metrics[-1]
    initial_supply = to_decimal(metrics[0].total_supply)
    final_supply = to_decimal(last_point.total_supply)
    
    # Ensure all values are Decimal using the helper function
    total_minted = to_decimal(last_point.total_minted)
    total_burned = to_decimal(last_point.total_burned)
    current_staked = to_decimal(last_point.staked_supply)
    
    # Calculate percentage change using only Decimal operations
    supply_change = (
        ((final_supply - initial_supply) * Decimal('100')) / initial_supply
        if initial_supply != Decimal('0')
        else Decimal('0')
    )
    
    # Create the metrics summary using the dataclass
    summary = MetricsSummary(
        final_supply=final_supply,
        total_minted=total_minted,
        total_burned=total_burned,
        current_staked=current_staked,
        supply_change_percentage=supply_change
    )
    
    # Convert to dictionary with guaranteed Decimal values
    return summary.to_dict() 