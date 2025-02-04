from decimal import Decimal
from typing import List
from app.models.tokenomics import (
    SupplyPoint, TokenPoint, VestingRequest, StakingRequest,
    VestingConfig, StakingConfig, VestingPeriod
)

def calculate_constant_inflation(
    initial_supply: Decimal,
    inflation_rate: Decimal,
    duration_in_years: int
) -> List[SupplyPoint]:
    """
    Calculate token supply evolution with constant inflation rate.
    
    Args:
        initial_supply: Initial token supply
        inflation_rate: Annual inflation rate (percentage)
        duration_in_years: Duration of simulation in years
        
    Returns:
        List of SupplyPoint containing year and supply for each period
    """
    simulation_data = []
    current_supply = initial_supply
    rate_multiplier = Decimal('1') + (inflation_rate / Decimal('100'))
    
    # Add initial point
    simulation_data.append(SupplyPoint(year=0, supply=current_supply))
    
    # Calculate supply for each year
    for year in range(1, duration_in_years + 1):
        current_supply = current_supply * rate_multiplier
        simulation_data.append(SupplyPoint(
            year=year,
            supply=current_supply.quantize(Decimal('0.00'))
        ))
    
    return simulation_data

def calculate_supply_increase(
    simulation_data: List[SupplyPoint]
) -> tuple[Decimal, Decimal]:
    """
    Calculate total supply increase in absolute and percentage terms.
    """
    if len(simulation_data) < 2:
        return Decimal('0'), Decimal('0')
        
    initial_supply = simulation_data[0].supply
    final_supply = simulation_data[-1].supply
    
    total_increase = final_supply - initial_supply
    percentage_increase = (total_increase / initial_supply * Decimal('100')).quantize(Decimal('0.00'))
    
    return total_increase.quantize(Decimal('0.00')), percentage_increase 

def simulate_vesting(request: VestingRequest) -> List[TokenPoint]:
    """Simulate token vesting over time."""
    timeline = []
    total_supply = request.initial_supply
    circulating_supply = request.initial_supply
    locked_supply = Decimal('0')
    
    # Calculate total vesting amount
    total_vesting = sum(period.amount for period in request.vesting_config.periods)
    
    # Initialize with vesting amount locked
    circulating_supply -= total_vesting
    locked_supply = total_vesting
    
    # Create initial point
    timeline.append(TokenPoint(
        month=0,
        total_supply=total_supply.quantize(Decimal('0.01')),
        circulating_supply=circulating_supply.quantize(Decimal('0.01')),
        locked_supply=locked_supply.quantize(Decimal('0.01')),
        burned_supply=Decimal('0'),
        staked_supply=Decimal('0'),
        rewards_distributed=Decimal('0')
    ))
    
    # Simulate each month
    for month in range(1, request.duration_in_months + 1):
        # Calculate vesting for this month
        vested_this_month = Decimal('0')
        
        for period in request.vesting_config.periods:
            if month < period.start_period:
                continue
                
            months_since_start = month - period.start_period
            
            if months_since_start < period.cliff_duration:
                continue
                
            if months_since_start >= period.duration:
                continue
                
            if period.release_type == "linear":
                # Calculate monthly vesting amount
                monthly_vesting = (
                    period.amount / Decimal(str(period.duration))
                ).quantize(Decimal('0.01'))
                
                if months_since_start == period.cliff_duration:
                    # Release cliff amount plus monthly vesting
                    vested_this_month += monthly_vesting * (period.cliff_duration + 1)
                else:
                    # Regular monthly vesting
                    vested_this_month += monthly_vesting
        
        # Ensure vesting doesn't exceed locked supply
        if vested_this_month > locked_supply:
            vested_this_month = locked_supply
            
        locked_supply -= vested_this_month
        circulating_supply += vested_this_month
        
        # Record point
        timeline.append(TokenPoint(
            month=month,
            total_supply=total_supply.quantize(Decimal('0.01')),
            circulating_supply=circulating_supply.quantize(Decimal('0.01')),
            locked_supply=locked_supply.quantize(Decimal('0.01')),
            burned_supply=Decimal('0'),
            staked_supply=Decimal('0'),
            rewards_distributed=Decimal('0')
        ))
    
    return timeline

def simulate_staking(request: StakingRequest) -> List[TokenPoint]:
    """Simulate token staking over time."""
    timeline = []
    total_supply = request.initial_supply
    circulating_supply = request.initial_supply
    staked_supply = Decimal('0')
    rewards_distributed = Decimal('0')
    
    # Calculate target staking amount
    target_staking = total_supply * (request.staking_config.target_rate / Decimal('100'))
    
    # Initialize with target staking
    staked_supply = target_staking
    circulating_supply -= target_staking
    
    # Create initial point
    timeline.append(TokenPoint(
        month=0,
        total_supply=total_supply.quantize(Decimal('0.01')),
        circulating_supply=circulating_supply.quantize(Decimal('0.01')),
        locked_supply=staked_supply.quantize(Decimal('0.01')),  # Staked tokens are considered locked
        burned_supply=Decimal('0'),
        staked_supply=staked_supply.quantize(Decimal('0.01')),
        rewards_distributed=Decimal('0')
    ))
    
    # Calculate monthly reward rate
    monthly_reward_rate = request.staking_config.reward_rate / Decimal('12')
    
    # Simulate each month
    for month in range(1, request.duration_in_months + 1):
        # Calculate and distribute rewards
        monthly_rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
        rewards_distributed += monthly_rewards
        total_supply += monthly_rewards
        
        # Calculate new target staking amount based on new total supply
        target_staking = total_supply * (request.staking_config.target_rate / Decimal('100'))
        
        # Add rewards to circulating supply first
        circulating_supply += monthly_rewards
        
        # Calculate how many additional tokens need to be staked
        staking_adjustment = target_staking - staked_supply
        
        if staking_adjustment > 0:
            # If we have enough circulating supply, stake up to the target
            stake_amount = min(staking_adjustment, circulating_supply)
            staked_supply += stake_amount
            circulating_supply -= stake_amount
        
        # Ensure staking never goes below target
        if staked_supply < target_staking and circulating_supply > 0:
            additional_stake = min(target_staking - staked_supply, circulating_supply)
            staked_supply += additional_stake
            circulating_supply -= additional_stake
        
        # Record point
        timeline.append(TokenPoint(
            month=month,
            total_supply=total_supply.quantize(Decimal('0.01')),
            circulating_supply=circulating_supply.quantize(Decimal('0.01')),
            locked_supply=staked_supply.quantize(Decimal('0.01')),  # Staked tokens are considered locked
            burned_supply=Decimal('0'),
            staked_supply=staked_supply.quantize(Decimal('0.01')),
            rewards_distributed=rewards_distributed.quantize(Decimal('0.01'))
        ))
    
    return timeline 