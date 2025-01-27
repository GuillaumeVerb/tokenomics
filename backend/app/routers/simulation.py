from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.models.tokenomics import (
    InflationSimulationRequest, InflationSimulationResponse,
    BurnSimulationRequest, VestingSimulationRequest, StakingSimulationRequest,
    TokenPoint, SimulationResponse
)
from app.models.scenario import ScenarioRequest, ScenarioResponse, PeriodMetrics
from app.models.comparison import (
    ComparisonRequest, ComparisonResponse,
    ScenarioComparison, ComparisonSummary, PlotlyGraph
)
from app.services.token_simulation_service import (
    simulate_burn, simulate_vesting, simulate_staking
)
from app.services.scenario_service import simulate_scenario

router = APIRouter()

@router.post("/constant_inflation", response_model=InflationSimulationResponse)
async def simulate_constant_inflation(request: InflationSimulationRequest):
    """Simulate constant inflation over time."""
    simulation_data = []
    current_supply = request.initial_supply
    total_increase = Decimal('0')
    
    for year in range(request.duration_in_years + 1):
        simulation_data.append({
            'year': year,
            'supply': current_supply
        })
        
        if year < request.duration_in_years:
            increase = current_supply * (request.inflation_rate / Decimal('100'))
            total_increase += increase
            current_supply += increase
    
    return {
        'simulation_data': simulation_data,
        'total_supply_increase': total_increase,
        'total_supply_increase_percentage': (total_increase / request.initial_supply * Decimal('100')).quantize(Decimal('0.01'))
    }

@router.post("/burn", response_model=SimulationResponse)
async def simulate_token_burn(request: BurnSimulationRequest):
    """Simulate token burning based on rate or events."""
    simulation_data = simulate_burn(request)
    
    # Calculate total burned amount
    total_burned = simulation_data[-1].burned_supply if simulation_data else Decimal('0')
    
    return {
        'simulation_data': simulation_data,
        'total_burned': total_burned
    }

@router.post("/vesting", response_model=SimulationResponse)
async def simulate_token_vesting(request: VestingSimulationRequest):
    """Simulate token vesting schedules."""
    simulation_data = simulate_vesting(request)
    
    # Calculate total vested amount
    total_vested = simulation_data[-1].circulating_supply if simulation_data else Decimal('0')
    
    return {
        'simulation_data': simulation_data,
        'total_vested': total_vested
    }

@router.post("/staking", response_model=SimulationResponse)
async def simulate_token_staking(request: StakingSimulationRequest):
    """Simulate token staking and rewards."""
    simulation_data = simulate_staking(request)
    
    # Get final metrics
    final_metrics = simulation_data[-1] if simulation_data else None
    
    return {
        'simulation_data': simulation_data,
        'total_staked': final_metrics.staked_supply if final_metrics else Decimal('0'),
        'total_rewards': final_metrics.rewards_distributed if final_metrics else Decimal('0')
    }

@router.post("/scenario", response_model=ScenarioResponse)
async def simulate_tokenomics_scenario(request: ScenarioRequest):
    """Simulate a complete tokenomics scenario."""
    return simulate_scenario(request)

@router.post("/compare", response_model=ComparisonResponse)
async def compare_scenarios(request: ComparisonRequest):
    """Compare multiple tokenomics scenarios."""
    # Simulate each scenario
    scenarios = []
    for scenario_request in request.scenarios:
        result = simulate_scenario(scenario_request)
        if not result:
            continue
            
        # Convert TokenPoint list to PeriodMetrics list
        timeline = [
            PeriodMetrics(
                period=point.month,
                total_supply=point.total_supply or Decimal('0'),
                circulating_supply=point.circulating_supply or Decimal('0'),
                locked_supply=point.locked_supply or Decimal('0'),
                burned_supply=point.burned_supply or Decimal('0'),
                staked_supply=point.staked_supply or Decimal('0'),
                rewards_distributed=point.rewards_distributed or Decimal('0')
            ) for point in result
        ]
        
        # Calculate summary from the last point
        last_point = result[-1]
        initial_supply = result[0].total_supply or Decimal('0')
        final_supply = last_point.total_supply or Decimal('0')
        
        summary = {
            'final_supply': final_supply,
            'total_minted': last_point.rewards_distributed or Decimal('0'),
            'total_burned': last_point.burned_supply or Decimal('0'),
            'current_staked': last_point.staked_supply or Decimal('0'),
            'supply_change_percentage': (
                ((final_supply - initial_supply) / initial_supply * Decimal('100'))
                if initial_supply > Decimal('0') else Decimal('0')
            ).quantize(Decimal('0.01'))
        }
        
        scenarios.append(ScenarioComparison(
            name=scenario_request.name,
            timeline=timeline,
            summary=summary
        ))
    
    if not scenarios:
        raise HTTPException(status_code=400, detail="No valid scenarios to compare")
    
    # Calculate comparison summary
    supply_range = {
        'min': min(s.summary['final_supply'] for s in scenarios),
        'max': max(s.summary['final_supply'] for s in scenarios)
    }
    minted_range = {
        'min': min(s.summary['total_minted'] for s in scenarios),
        'max': max(s.summary['total_minted'] for s in scenarios)
    }
    burned_range = {
        'min': min(s.summary['total_burned'] for s in scenarios),
        'max': max(s.summary['total_burned'] for s in scenarios)
    }
    staked_range = {
        'min': min(s.summary['current_staked'] for s in scenarios),
        'max': max(s.summary['current_staked'] for s in scenarios)
    }
    supply_change_range = {
        'min': min(s.summary['supply_change_percentage'] for s in scenarios),
        'max': max(s.summary['supply_change_percentage'] for s in scenarios)
    }
    
    comparison_summary = ComparisonSummary(
        supply_range=supply_range,
        minted_range=minted_range,
        burned_range=burned_range,
        staked_range=staked_range,
        supply_change_range=supply_change_range
    )
    
    # Generate combined graph if requested
    combined_graph = None
    if request.return_combined_graph and request.metrics_to_graph:
        graph_data = []
        for scenario in scenarios:
            for metric in request.metrics_to_graph:
                graph_data.append({
                    'x': [m.period for m in scenario.timeline],
                    'y': [getattr(m, metric) for m in scenario.timeline],
                    'name': f"{scenario.name} - {metric}",
                    'type': 'scatter'
                })
        
        graph_layout = {
            'title': 'Scenario Comparison',
            'xaxis': {'title': 'Period'},
            'yaxis': {'title': 'Amount'},
            'legend': {'orientation': 'h', 'y': -0.2}
        }
        
        combined_graph = PlotlyGraph(data=graph_data, layout=graph_layout)
    
    return ComparisonResponse(
        scenarios=scenarios,
        summary=comparison_summary,
        combined_graph=combined_graph
    ) 