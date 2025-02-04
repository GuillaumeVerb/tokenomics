from decimal import Decimal
from typing import List, Dict
from app.models.tokenomics import (
    TokenPoint, BurnEvent, VestingPeriod,
    BurnRequest, VestingRequest, StakingRequest
)

def simulate_burn(request: BurnRequest) -> List[TokenPoint]:
    """Simulate token burning based on rate or specific events."""
    simulation_data = []
    current_supply = request.initial_supply
    total_burned = Decimal('0')
    
    for month in range(request.duration_in_months + 1):
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

def simulate_vesting(request: VestingRequest) -> List[TokenPoint]:
    """Simulate token vesting with optional cliff periods."""
    vesting_schedule = [Decimal('0')] * (request.duration_in_months + 1)
    locked_supply = Decimal('0')
    circulating_supply = request.initial_supply

    for period in request.vesting_config.periods:
        # Calculate monthly vesting amount for linear distribution after cliff
        remaining_months = period.duration - period.cliff_duration
        if remaining_months > 0:
            # Calculate monthly amount based on remaining months after cliff
            monthly_amount = period.amount / Decimal(str(remaining_months))
        else:
            # If no remaining months, all tokens are released at cliff
            monthly_amount = period.amount

        # Lock tokens initially
        locked_supply += period.amount
        circulating_supply -= period.amount

        # Handle cliff release
        if period.cliff_duration > 0:
            cliff_month = period.start_period + period.cliff_duration
            if cliff_month <= request.duration_in_months:
                if remaining_months > 0:
                    # No tokens released at cliff - they will be released linearly
                    pass
                else:
                    # Release all tokens at cliff if no linear vesting
                    vesting_schedule[cliff_month] += period.amount

        # Add linear vesting after cliff
        if remaining_months > 0:
            start = period.start_period + period.cliff_duration + 1
            end = min(period.start_period + period.duration, request.duration_in_months)
            for month in range(start, end + 1):
                vesting_schedule[month] += monthly_amount

    # Generate simulation data
    simulation_data = []
    vested_amount = Decimal('0')
    for month in range(request.duration_in_months + 1):
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

def simulate_staking(request: StakingRequest) -> List[TokenPoint]:
    """Simulate token staking with rewards."""
    # Initialize variables
    circulating_supply = request.initial_supply
    staked_supply = Decimal('0')
    locked_supply = Decimal('0')
    rewards_distributed = Decimal('0')
    
    # Calculate target staking amount
    target_staking = request.initial_supply * request.staking_config.target_rate / Decimal('100')
    
    # Calculate monthly reward rate
    monthly_reward_rate = request.staking_config.reward_rate / Decimal('12')
    
    # Generate simulation data
    simulation_data = []
    for month in range(request.duration_in_months + 1):
        if month == 0:
            # Initial staking
            staked_supply = target_staking
            locked_supply = staked_supply
            circulating_supply -= staked_supply
        else:
            # Calculate and distribute rewards
            monthly_rewards = staked_supply * monthly_reward_rate / Decimal('100')
            rewards_distributed += monthly_rewards
            circulating_supply += monthly_rewards
            
            # Handle unlocking after lock period
            if month >= request.staking_config.lock_duration:
                unlock_amount = staked_supply * Decimal('0.1')  # 10% monthly unlock rate
                staked_supply -= unlock_amount
                locked_supply -= unlock_amount
                circulating_supply += unlock_amount
        
        simulation_data.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply.quantize(Decimal('0.01')),
                locked_supply=locked_supply.quantize(Decimal('0.01')),
                burned_supply=None,
                staked_supply=staked_supply.quantize(Decimal('0.01')),
                rewards_distributed=rewards_distributed.quantize(Decimal('0.01'))
            )
        )
    
    return simulation_data 