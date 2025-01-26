from fastapi import APIRouter, HTTPException
from app.models.tokenomics import (
    InflationSimulationRequest,
    InflationSimulationResponse,
    BurnSimulationRequest,
    VestingSimulationRequest,
    StakingSimulationRequest,
    SimulationResponse
)
from app.services.simulation_service import (
    calculate_constant_inflation,
    calculate_supply_increase
)
from app.services.token_simulation_service import simulate_burn, simulate_vesting, simulate_staking
from decimal import Decimal
from typing import List, Dict
from ..models.scenario import (
    ScenarioRequest, ScenarioResponse, PeriodMetrics, ScenarioSummary
)
from ..models.comparison import (
    ComparisonRequest, ComparisonResponse, ScenarioComparison,
    ComparisonSummary, PlotlyGraph
)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    period: int,
    config: dict,
    time_step: str
) -> Decimal:
    if not config:
        return Decimal(0)
        
    rate = config.initial_rate
    
    # Adjust rate based on type
    if config.type == "halving":
        halvings = period // config.halving_period
        rate = rate / (2 ** halvings)
    elif config.type == "dynamic":
        rate = max(
            config.min_rate,
            rate * (1 - config.decay_rate/100) ** period
        )
    
    # Convert annual rate to monthly if needed
    if time_step == "monthly":
        rate = rate / 12
        
    return current_supply * (rate / 100)

def calculate_burn(
    current_supply: Decimal,
    period: int,
    config: dict,
    time_step: str
) -> Decimal:
    if not config:
        return Decimal(0)
        
    if config.type == "continuous":
        rate = config.rate / 12 if time_step == "monthly" else config.rate
        return current_supply * (rate / 100)
    else:
        return sum(
            event.amount 
            for event in config.events 
            if event.period == period
        )

def calculate_vesting(
    period: int,
    config: dict
) -> Decimal:
    if not config:
        return Decimal(0)
        
    total_vested = Decimal(0)
    
    for vest_period in config.periods:
        if period < vest_period.start_period:
            continue
            
        relative_period = period - vest_period.start_period
        
        if relative_period < vest_period.cliff_duration:
            continue
            
        if relative_period >= vest_period.duration:
            continue
            
        if vest_period.release_type == "linear":
            vesting_rate = Decimal(1) / (vest_period.duration - vest_period.cliff_duration)
            period_vested = vest_period.amount * vesting_rate
        else:  # exponential
            remaining_periods = vest_period.duration - vest_period.cliff_duration
            vesting_rate = Decimal(2) / (remaining_periods * (remaining_periods + 1))
            period_number = relative_period - vest_period.cliff_duration + 1
            period_vested = vest_period.amount * vesting_rate * period_number
            
        total_vested += period_vested
        
    return total_vested

def calculate_staking(
    circulating_supply: Decimal,
    period: int,
    config: dict,
    time_step: str
) -> tuple[Decimal, Decimal]:
    if not config or not config.enabled:
        return Decimal(0), Decimal(0)
        
    target_staked = circulating_supply * (config.target_rate / 100)
    
    # Convert annual rate to monthly if needed
    reward_rate = config.reward_rate / 12 if time_step == "monthly" else config.reward_rate
    rewards = target_staked * (reward_rate / 100)
    
    return target_staked, rewards

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
        request.initial_supply,
        0,
        request.staking_config,
        request.time_step
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
            period,
            request.inflation_config,
            request.time_step
        )
        total_supply += minted
        total_minted += minted
        
        # 2. Calculate burn
        burned = calculate_burn(
            total_supply,
            period,
            request.burn_config,
            request.time_step
        )
        total_supply -= burned
        total_burned += burned
        
        # 3. Calculate vesting
        vested = calculate_vesting(period, request.vesting_config)
        total_vested += vested
        
        # 4. Calculate staking
        staked_amount, staking_rewards = calculate_staking(
            total_supply - staked_amount,
            period,
            request.staking_config,
            request.time_step
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