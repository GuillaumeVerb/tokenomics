from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.models.tokenomics import (
    ConstantInflationRequest, InflationSimulationResponse,
    BurnRequest, VestingRequest, StakingRequest,
    TokenPoint, SimulationResponse, ScenarioRequest,
    ScenarioResponse, PeriodMetrics, ComparisonRequest,
    ComparisonResponse, ScenarioSummary, ComparisonSummary
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
from app.services.simulation_service import (
    calculate_constant_inflation, calculate_supply_increase
)

router = APIRouter()

@router.post("/constant_inflation", response_model=InflationSimulationResponse)
async def simulate_constant_inflation(request: ConstantInflationRequest):
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
async def simulate_token_burn(request: BurnRequest):
    """Simulate token burning based on rate or events."""
    simulation_data = simulate_burn(request)
    
    # Calculate total burned amount
    total_burned = simulation_data[-1].burned_supply if simulation_data else Decimal('0')
    
    return {
        'simulation_data': simulation_data,
        'total_burned': total_burned
    }

@router.post("/vesting", response_model=SimulationResponse)
async def simulate_token_vesting(request: VestingRequest):
    """Simulate token vesting schedules."""
    simulation_data = simulate_vesting(request)
    
    # Calculate total vested amount
    total_vested = simulation_data[-1].circulating_supply if simulation_data else Decimal('0')
    
    return {
        'simulation_data': simulation_data,
        'total_vested': total_vested
    }

@router.post("/staking", response_model=SimulationResponse)
async def simulate_token_staking(request: StakingRequest):
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
    timeline = []
    total_supply = request.initial_supply
    circulating_supply = request.initial_supply
    total_minted = Decimal('0')
    total_burned = Decimal('0')
    total_vested = Decimal('0')
    total_staking_rewards = Decimal('0')
    staked_supply = Decimal('0')
    locked_supply = Decimal('0')
    
    # Initialize first period
    if request.staking_config and request.staking_config.enabled:
        target_staking = total_supply * (request.staking_config.target_rate / Decimal('100'))
        staked_supply = target_staking
        circulating_supply -= staked_supply
        locked_supply = staked_supply
    
    timeline.append(PeriodMetrics(
        period=0,
        total_supply=total_supply,
        circulating_supply=circulating_supply,
        minted_amount=Decimal('0'),
        burned_amount=Decimal('0'),
        vested_amount=Decimal('0'),
        staked_amount=staked_supply,
        staking_rewards=Decimal('0'),
        locked_amount=locked_supply
    ))
    
    # Simulate each period
    for month in range(1, request.duration + 1):
        period_minted = Decimal('0')
        period_burned = Decimal('0')
        period_vested = Decimal('0')
        period_staking_rewards = Decimal('0')
        
        # 1. Calculate inflation
        if request.inflation_config:
            if request.inflation_config.type == "constant":
                period_minted = total_supply * (request.inflation_config.initial_rate / Decimal('1200'))
            elif request.inflation_config.type == "dynamic":
                current_rate = max(
                    request.inflation_config.initial_rate * (1 - request.inflation_config.decay_rate / Decimal('100')) ** month,
                    request.inflation_config.min_rate
                )
                period_minted = total_supply * (current_rate / Decimal('1200'))
            elif request.inflation_config.type == "halving":
                if month % request.inflation_config.halving_period == 0:
                    request.inflation_config.initial_rate /= 2
                period_minted = total_supply * (request.inflation_config.initial_rate / Decimal('1200'))
        
        total_supply += period_minted
        circulating_supply += period_minted
        total_minted += period_minted
        
        # 2. Calculate burn
        if request.burn_config:
            if request.burn_config.type == "continuous":
                period_burned = circulating_supply * (request.burn_config.rate / Decimal('1200'))
        
        total_supply -= period_burned
        circulating_supply -= period_burned
        total_burned += period_burned
        
        # 3. Calculate vesting
        if request.vesting_config:
            for period in request.vesting_config.periods:
                if month < period.start_period:
                    continue
                
                months_since_start = month - period.start_period
                
                if months_since_start < period.cliff_duration:
                    continue
                
                if months_since_start >= period.duration:
                    continue
                
                if period.release_type == "linear":
                    if months_since_start == period.cliff_duration:
                        # Release cliff amount
                        period_vested += (
                            period.amount * 
                            Decimal(str(period.cliff_duration)) / 
                            Decimal(str(period.duration))
                        )
                    else:
                        # Linear release after cliff
                        remaining_months = period.duration - period.cliff_duration
                        if remaining_months > 0:
                            monthly_amount = (
                                period.amount * 
                                (1 - Decimal(str(period.cliff_duration)) / Decimal(str(period.duration))) /
                                Decimal(str(remaining_months))
                            )
                            period_vested += monthly_amount
        
        # Ensure vesting doesn't exceed locked supply
        if period_vested > locked_supply:
            period_vested = locked_supply
            
        locked_supply -= period_vested
        circulating_supply += period_vested
        total_vested += period_vested
        
        # 4. Calculate staking
        if request.staking_config and request.staking_config.enabled:
            # Calculate and distribute rewards
            monthly_reward_rate = request.staking_config.reward_rate / Decimal('12')
            period_staking_rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
            
            total_supply += period_staking_rewards
            circulating_supply += period_staking_rewards
            total_minted += period_staking_rewards
            total_staking_rewards += period_staking_rewards
            
            # Update staking based on new total supply
            target_staking = total_supply * (request.staking_config.target_rate / Decimal('100'))
            staking_adjustment = target_staking - staked_supply
            
            if staking_adjustment > 0:
                stake_amount = min(staking_adjustment, circulating_supply)
                staked_supply += stake_amount
                circulating_supply -= stake_amount
                locked_supply += stake_amount
        
        # Record period metrics
        timeline.append(PeriodMetrics(
            period=month,
            total_supply=total_supply,
            circulating_supply=circulating_supply,
            minted_amount=period_minted,
            burned_amount=period_burned,
            vested_amount=period_vested,
            staked_amount=staked_supply,
            staking_rewards=period_staking_rewards,
            locked_amount=locked_supply
        ))
    
    # Calculate summary
    supply_change = ((total_supply - request.initial_supply) / request.initial_supply * 100)
    
    summary = ScenarioSummary(
        final_supply=total_supply,
        total_minted=total_minted,
        total_burned=total_burned,
        total_vested=total_vested,
        total_staking_rewards=total_staking_rewards,
        current_staked=staked_supply,
        current_locked=locked_supply,
        supply_change_percentage=supply_change
    )
    
    return ScenarioResponse(timeline=timeline, summary=summary)

@router.post("/compare", response_model=ComparisonResponse)
async def compare_scenarios(request: ComparisonRequest):
    """Compare multiple tokenomics scenarios."""
    # Simulate each scenario
    scenarios = []
    for scenario_request in request.scenarios:
        result = await simulate_tokenomics_scenario(scenario_request)
        if not result:
            continue
            
        # Convert timeline to PeriodMetrics list
        timeline = []
        for point in result.timeline:
            timeline.append(PeriodMetrics(
                period=point.period,
                total_supply=point.total_supply,
                circulating_supply=point.circulating_supply,
                minted_amount=point.minted_amount,
                burned_amount=point.burned_amount,
                vested_amount=point.vested_amount,
                staked_amount=point.staked_amount,
                staking_rewards=point.staking_rewards,
                locked_amount=point.locked_amount
            ))
        
        # Calculate summary from the last point
        last_point = result.timeline[-1]
        initial_supply = result.timeline[0].total_supply
        final_supply = last_point.total_supply
        
        summary = {
            'final_supply': final_supply,
            'total_minted': last_point.minted_amount,
            'total_burned': last_point.burned_amount,
            'current_staked': last_point.staked_amount,
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
    
    comparison_summary = ComparisonSummary(
        supply_range=supply_range,
        minted_range=minted_range,
        burned_range=burned_range,
        staked_range=staked_range
    )
    
    return ComparisonResponse(
        scenarios=scenarios,
        summary=comparison_summary,
        combined_graph=None
    ) 