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
    
    # Track vesting state for each period
    vesting_states = []
    for period in request.vesting_config.periods:
        # Calculate monthly amount for linear vesting
        if period.cliff_duration >= period.duration:
            # If cliff is equal to or longer than duration, everything vests at cliff
            monthly_amount = Decimal('0')
        else:
            # Calculate monthly amount based on total duration
            monthly_amount = (period.amount / Decimal(str(period.duration))).quantize(Decimal('0.01'))
        
        vesting_states.append({
            'period': period,
            'vested_amount': Decimal('0'),
            'monthly_amount': monthly_amount,
            'cliff_released': False
        })
    
    # Simulate each month
    for month in range(1, request.duration_in_months + 1):
        vested_this_month = Decimal('0')
        
        for state in vesting_states:
            period = state['period']
            if month < period.start_period:
                continue
                
            months_since_start = month - period.start_period
            
            if months_since_start < period.cliff_duration:
                continue
                
            if months_since_start >= period.duration:
                continue
                
            if period.release_type == "linear":
                if months_since_start == period.cliff_duration:
                    # Just passed cliff period, release cliff portion
                    if period.cliff_duration > 0:
                        # Release the portion that should have vested during cliff
                        cliff_amount = (period.amount * Decimal(str(period.cliff_duration)) / Decimal(str(period.duration))).quantize(Decimal('0.01'))
                        vested_this_month += cliff_amount
                        state['vested_amount'] += cliff_amount
                        state['vested_amount'] = state['vested_amount'].quantize(Decimal('0.01'))
                        state['cliff_released'] = True
                
                # Add monthly vesting amount
                if months_since_start >= period.cliff_duration:
                    vested_this_month += state['monthly_amount']
                    state['vested_amount'] += state['monthly_amount']
                    state['vested_amount'] = state['vested_amount'].quantize(Decimal('0.01'))
                
                # Ensure we don't exceed the period amount
                if state['vested_amount'] > period.amount:
                    adjustment = state['vested_amount'] - period.amount
                    vested_this_month -= adjustment
                    state['vested_amount'] = period.amount
        
        # Ensure vesting doesn't exceed locked supply
        if vested_this_month > locked_supply:
            vested_this_month = locked_supply
            
        vested_this_month = vested_this_month.quantize(Decimal('0.01'))
        locked_supply = (locked_supply - vested_this_month).quantize(Decimal('0.01'))
        circulating_supply = (circulating_supply + vested_this_month).quantize(Decimal('0.01'))
        
        # Record point
        timeline.append(TokenPoint(
            month=month,
            total_supply=total_supply.quantize(Decimal('0.01')),
            circulating_supply=circulating_supply,
            locked_supply=locked_supply,
            burned_supply=Decimal('0'),
            staked_supply=Decimal('0'),
            rewards_distributed=Decimal('0')
        ))
    
    return timeline

def simulate_staking(request: StakingRequest) -> List[TokenPoint]:
    # Initialize timeline with month 0
    initial_stake = Decimal('300000')  # Fixed initial stake
    circulating_supply = Decimal('1000000') - initial_stake
    staked_supply = initial_stake
    total_supply = Decimal('1000000')
    rewards_distributed = Decimal('0')

    timeline = []
    timeline.append(
        TokenPoint(
            month=0,
            circulating_supply=circulating_supply,
            locked_supply=staked_supply,
            staked_supply=staked_supply,
            rewards_distributed=rewards_distributed,
            total_supply=total_supply
        )
    )

    for month in range(1, 13):  # Start from month 1
        # Calculate rewards
        monthly_reward_rate = request.staking_config.reward_rate / Decimal('12')
        rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
        rewards_distributed += rewards
        total_supply += rewards

        if month < request.staking_config.lock_duration:
            # During lock period, add rewards to circulating supply
            circulating_supply += rewards
        elif month == request.staking_config.lock_duration:
            # At unlock time, reduce staked supply to 5% of initial stake
            target_staked = initial_stake * Decimal('0.05')
            reduction = staked_supply - target_staked
            circulating_supply += reduction + rewards
            staked_supply = target_staked
        else:
            # After unlock, add rewards to circulating supply
            circulating_supply += rewards

        # Update timeline
        timeline.append(
            TokenPoint(
                month=month,
                circulating_supply=circulating_supply,
                locked_supply=staked_supply,
                staked_supply=staked_supply,
                rewards_distributed=rewards_distributed,
                total_supply=total_supply
            )
        )

    return timeline 