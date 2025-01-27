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
    
    for month in range(request.duration + 1):
        # Calculate burn for this month
        monthly_burn = Decimal('0')
        
        # Calculate continuous burn if rate is specified
        if request.burn_rate:
            monthly_burn = current_supply * (request.burn_rate / Decimal('100'))
        
        # Add specific burn events
        if request.burn_events:
            month_burns = sum(
                event.amount for event in request.burn_events 
                if event.month == month
            )
            monthly_burn += month_burns
        
        # Apply burns after calculating total for the month
        if month > 0:  # Don't burn in the initial month
            total_burned += monthly_burn
            current_supply -= monthly_burn
        
        simulation_data.append(TokenPoint(
            month=month,
            circulating_supply=current_supply.quantize(Decimal('0.00')),
            burned_supply=total_burned.quantize(Decimal('0.00'))
        ))
    
    return simulation_data

def simulate_vesting(request: VestingSimulationRequest) -> List[TokenPoint]:
    """Simulate token vesting with optional cliff periods."""
    vesting_schedule = [Decimal('0')] * (request.duration + 1)
    locked_supply = Decimal('0')
    circulating_supply = request.total_supply

    for period in request.vesting_periods:
        # Calculate monthly vesting amount for linear distribution after cliff
        remaining_months = period.duration_months - period.cliff_months
        if remaining_months > 0:
            # Calculate monthly amount based on remaining months after cliff
            monthly_amount = period.tokens_amount / Decimal(str(remaining_months))
        else:
            # If no remaining months, all tokens are released at cliff
            monthly_amount = period.tokens_amount

        # Lock tokens initially
        locked_supply += period.tokens_amount
        circulating_supply -= period.tokens_amount

        # Handle cliff release
        if period.cliff_months > 0:
            cliff_month = period.start_month + period.cliff_months
            if cliff_month <= request.duration:
                if remaining_months > 0:
                    # No tokens released at cliff - they will be released linearly
                    pass
                else:
                    # Release all tokens at cliff if no linear vesting
                    vesting_schedule[cliff_month] += period.tokens_amount

        # Add linear vesting after cliff
        if remaining_months > 0:
            start = period.start_month + period.cliff_months + 1
            end = min(period.start_month + period.duration_months, request.duration)
            for month in range(start, end + 1):
                vesting_schedule[month] += monthly_amount

    # Generate simulation data
    simulation_data = []
    for month in range(request.duration + 1):
        if month > 0:
            vested_amount = vesting_schedule[month]
            locked_supply -= vested_amount
            circulating_supply += vested_amount

        simulation_data.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply.quantize(Decimal('0.01')),
                locked_supply=locked_supply.quantize(Decimal('0.01')),
                burned_supply=None,
                staked_supply=None,
                rewards_distributed=None
            )
        )

    return simulation_data

def simulate_staking(request: StakingSimulationRequest) -> List[TokenPoint]:
    """Simulate token staking and rewards distribution."""
    simulation_data = []
    circulating_supply = request.total_supply
    staked_supply = Decimal('0')
    total_rewards = Decimal('0')
    
    # Convert annual rates to monthly
    monthly_reward_rate = request.staking_reward_rate / Decimal('12')
    target_staked = request.total_supply * (request.staking_rate / Decimal('100'))
    monthly_staking_growth = Decimal('0.40')  # 40% monthly growth towards target
    
    for month in range(request.duration + 1):
        if month > 0:
            # Calculate and distribute rewards
            monthly_rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
            total_rewards += monthly_rewards
            circulating_supply += monthly_rewards
            
            if month <= request.lock_period:
                # During lock period, aggressively stake towards target
                if staked_supply < target_staked:
                    available_for_staking = circulating_supply - staked_supply
                    gap_to_target = target_staked - staked_supply
                    staking_increase = min(
                        gap_to_target * monthly_staking_growth,
                        available_for_staking * monthly_staking_growth,
                        gap_to_target  # Never exceed target
                    )
                    if staking_increase > Decimal('0'):
                        staked_supply += staking_increase
                        circulating_supply -= staking_increase
            else:
                # After lock period, unstake a small portion and then restake aggressively
                unstaking_amount = staked_supply * Decimal('0.08')  # 8% unstaking
                staked_supply -= unstaking_amount
                circulating_supply += unstaking_amount
                
                # Try to stake back up to target plus a buffer
                target_with_buffer = target_staked * Decimal('1.05')  # Target + 5%
                available_for_staking = circulating_supply - staked_supply
                gap_to_target = target_with_buffer - staked_supply
                staking_increase = min(
                    gap_to_target * Decimal('0.75'),  # 75% of gap
                    available_for_staking * Decimal('0.75'),  # 75% of available
                    gap_to_target  # Never exceed target
                )
                if staking_increase > Decimal('0'):
                    staked_supply += staking_increase
                    circulating_supply -= staking_increase
        
        simulation_data.append(TokenPoint(
            month=month,
            circulating_supply=circulating_supply.quantize(Decimal('0.01')),
            staked_supply=staked_supply.quantize(Decimal('0.01')),
            rewards_distributed=total_rewards.quantize(Decimal('0.01')),
            locked_supply=None,
            burned_supply=None
        ))
    
    return simulation_data 