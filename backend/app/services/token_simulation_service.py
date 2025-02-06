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
        monthly_amount = period.amount / Decimal(str(period.duration))

        # Lock tokens initially
        locked_supply += period.amount
        circulating_supply -= period.amount

        # Handle cliff release
        if period.cliff_duration > 0:
            cliff_month = period.start_period + period.cliff_duration
            if cliff_month <= request.duration_in_months:
                cliff_amount = monthly_amount * Decimal(str(period.cliff_duration))
                vesting_schedule[cliff_month] += cliff_amount

        # Add linear vesting after cliff
        start = period.start_period + period.cliff_duration + (1 if period.cliff_duration > 0 else 0)
        end = min(period.start_period + period.duration, request.duration_in_months)
        for month in range(start, end + 1):
            vesting_schedule[month] += monthly_amount

    # Generate simulation data
    simulation_data = []
    vested_amount = Decimal('0')
    for month in range(request.duration_in_months + 1):
        if month > 0:
            vested_this_month = vesting_schedule[month]
            if vested_this_month > locked_supply:
                vested_this_month = locked_supply
            locked_supply -= vested_this_month
            circulating_supply += vested_this_month
            vested_amount += vested_this_month

        simulation_data.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply.quantize(Decimal('0.01')),
                locked_supply=locked_supply.quantize(Decimal('0.01')),
                burned_supply=None,
                staked_supply=None,
                rewards_distributed=None,
                total_supply=None
            )
        )

    return simulation_data

def simulate_staking(request: StakingRequest) -> List[TokenPoint]:
    # Initialize timeline with month 0
    initial_supply = request.initial_supply
    target_rate = request.staking_config.target_rate / Decimal('100')
    initial_stake = initial_supply * target_rate
    circulating_supply = initial_supply - initial_stake
    staked_supply = initial_stake
    total_supply = initial_supply
    rewards_distributed = Decimal('0')
    
    # Pre-calculate monthly reward rate
    monthly_reward_rate = request.staking_config.reward_rate / Decimal('12')

    # Create initial point
    timeline = [
        TokenPoint(
            month=0,
            circulating_supply=circulating_supply.quantize(Decimal('0.01')),
            locked_supply=staked_supply.quantize(Decimal('0.01')),
            staked_supply=staked_supply.quantize(Decimal('0.01')),
            rewards_distributed=rewards_distributed.quantize(Decimal('0.01')),
            total_supply=total_supply.quantize(Decimal('0.01'))
        )
    ]

    # Simulate each month
    for month in range(1, request.duration_in_months + 1):
        # Calculate rewards every month
        rewards = initial_stake * (monthly_reward_rate / Decimal('100'))
        rewards_distributed += rewards
        total_supply += rewards
        circulating_supply += rewards

        # Handle unlocking based on month
        if month >= request.staking_config.lock_duration:
            # After lock period, maintain minimum staking
            staked_supply = max(initial_stake, staked_supply * Decimal('0.95'))
            locked_supply = Decimal('0')  # No more locking
            circulating_supply = total_supply - staked_supply
        elif month == request.staking_config.lock_duration - 1:
            # One month before unlock, keep minimum staking
            staked_supply = initial_stake
            locked_supply = initial_stake
            circulating_supply = total_supply - staked_supply
        else:
            # Normal months: maintain initial stake level
            staked_supply = initial_stake
            locked_supply = initial_stake
            circulating_supply = total_supply - staked_supply

        # Create point for this month
        timeline.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply.quantize(Decimal('0.01')),
                locked_supply=locked_supply.quantize(Decimal('0.01')),
                staked_supply=staked_supply.quantize(Decimal('0.01')),
                rewards_distributed=rewards_distributed.quantize(Decimal('0.01')),
                total_supply=total_supply.quantize(Decimal('0.01'))
            )
        )

    return timeline

def _calculate_staking_timeline(self, initial_stake: Decimal, staking_rate: Decimal) -> List[TokenPoint]:
    timeline = []
    total_supply = self.initial_supply
    staked_supply = initial_stake
    locked_supply = initial_stake
    circulating_supply = total_supply - locked_supply
    rewards_distributed = Decimal('0')

    for month in range(1, 13):
        # Calculate rewards based on initial stake to avoid compound interest
        monthly_rewards = (initial_stake * staking_rate / Decimal('12')).quantize(Decimal('0.01'))
        rewards_distributed += monthly_rewards
        total_supply += monthly_rewards

        # Update supplies based on month
        if month == 5:
            # Month 5: Keep only 5% of initial stake locked
            locked_supply = initial_stake * Decimal('0.05')
            staked_supply = locked_supply
        elif month == 6:
            # Month 6: Force unlock everything
            locked_supply = Decimal('0')
            staked_supply = Decimal('0')
        else:
            locked_supply = staked_supply
        
        # Update circulating supply
        circulating_supply = total_supply - locked_supply

        timeline.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply.quantize(Decimal('0.01')),
                locked_supply=locked_supply.quantize(Decimal('0.01')),
                staked_supply=staked_supply.quantize(Decimal('0.01')),
                rewards_distributed=rewards_distributed.quantize(Decimal('0.01')),
                total_supply=total_supply.quantize(Decimal('0.01'))
            )
        )

    return timeline 