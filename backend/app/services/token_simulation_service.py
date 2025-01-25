from decimal import Decimal
from typing import List, Dict
from app.models.tokenomics import (
    TokenPoint, BurnEvent, VestingPeriod,
    BurnSimulationRequest, VestingSimulationRequest, StakingSimulationRequest
)

def simulate_burn(request: BurnSimulationRequest) -> List[TokenPoint]:
    """Simulate token burning based on rate or specific events."""
    simulation_data = []
    current_supply = request.initial_supply
    total_burned = Decimal('0')
    
    for month in range(request.duration_in_months + 1):
        # Calculate continuous burn if rate is specified
        if request.burn_rate:
            monthly_burn = current_supply * (request.burn_rate / Decimal('100'))
            total_burned += monthly_burn
            current_supply -= monthly_burn
        
        # Add specific burn events
        if request.burn_events:
            month_burns = sum(
                event.amount for event in request.burn_events 
                if event.month == month
            )
            total_burned += month_burns
            current_supply -= month_burns
        
        simulation_data.append(TokenPoint(
            month=month,
            circulating_supply=current_supply.quantize(Decimal('0.00')),
            burned_supply=total_burned.quantize(Decimal('0.00'))
        ))
    
    return simulation_data

def simulate_vesting(request: VestingSimulationRequest) -> List[TokenPoint]:
    """Simulate token vesting for multiple periods."""
    simulation_data = []
    locked_supply = request.total_supply
    vested_amounts = {0: Decimal('0')}  # Month -> amount vested that month
    
    # Calculate vesting schedule
    for period in request.vesting_periods:
        monthly_release = period.tokens_amount / Decimal(str(period.duration_months))
        for month in range(
            period.start_month + period.cliff_months,
            period.start_month + period.duration_months
        ):
            if month not in vested_amounts:
                vested_amounts[month] = Decimal('0')
            vested_amounts[month] += monthly_release
    
    # Generate simulation data
    cumulative_vested = Decimal('0')
    for month in range(request.duration_in_months + 1):
        if month in vested_amounts:
            cumulative_vested += vested_amounts[month]
        locked_supply = request.total_supply - cumulative_vested
        
        simulation_data.append(TokenPoint(
            month=month,
            circulating_supply=cumulative_vested.quantize(Decimal('0.00')),
            locked_supply=locked_supply.quantize(Decimal('0.00'))
        ))
    
    return simulation_data

def simulate_staking(request: StakingSimulationRequest) -> List[TokenPoint]:
    """Simulate token staking and rewards distribution."""
    simulation_data = []
    circulating_supply = request.total_supply
    staked_supply = Decimal('0')
    total_rewards = Decimal('0')
    
    # Convert annual rate to monthly
    monthly_reward_rate = request.staking_reward_rate / Decimal('12')
    expected_staked = request.total_supply * (request.staking_rate / Decimal('100'))
    
    for month in range(request.duration_in_months + 1):
        # Calculate staking changes
        if month > 0:
            # Calculate and distribute rewards
            monthly_rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
            total_rewards += monthly_rewards
            circulating_supply += monthly_rewards
            
            # Adjust staked amount towards expected rate
            staking_delta = (expected_staked - staked_supply) / Decimal('12')
            staked_supply += staking_delta
        
        simulation_data.append(TokenPoint(
            month=month,
            circulating_supply=circulating_supply.quantize(Decimal('0.00')),
            staked_supply=staked_supply.quantize(Decimal('0.00')),
            rewards_distributed=total_rewards.quantize(Decimal('0.00'))
        ))
    
    return simulation_data 