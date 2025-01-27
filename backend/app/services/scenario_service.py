from decimal import Decimal
from typing import List, Optional, Union, cast, Any
from app.models.scenario import (
    ScenarioRequest, ScenarioResponse,
    PeriodMetrics, ScenarioSummary,
    InflationConfig, BurnConfig, VestingConfig, StakingConfig
)
from app.models.tokenomics import ScenarioRequest
from app.models.simulation import TokenPoint

def to_decimal(value: Union[int, float, Decimal, None]) -> Decimal:
    """Convert a value to Decimal, returning Decimal('0') for None."""
    if value is None:
        return cast(Decimal, Decimal('0'))
    return cast(Decimal, Decimal(str(value)))

def calculate_inflation(
    current_supply: Decimal,
    config: InflationConfig,
    period: int,
    is_monthly: bool
) -> Decimal:
    """Calculate inflation for a given period."""
    if not config or not config.initial_rate:
        return cast(Decimal, Decimal('0'))
        
    if config.type == "constant":
        rate = to_decimal(config.initial_rate)
    elif config.type == "halving":
        halving_period = int(config.halving_period or 1)
        halvings = period // (halving_period * (12 if is_monthly else 1))
        rate = to_decimal(config.initial_rate) / cast(Decimal, Decimal(str(2 ** halvings)))
    else:  # dynamic
        min_rate = to_decimal(config.min_rate)
        decay_rate = to_decimal(config.decay_rate)
        decay = decay_rate / cast(Decimal, Decimal(str(12 if is_monthly else 1)))
        rate = cast(Decimal, max(
            min_rate,
            to_decimal(config.initial_rate) * ((cast(Decimal, Decimal('1')) - decay/cast(Decimal, Decimal('100'))) ** period)
        ))
    
    # Convert annual rate to monthly if needed
    if is_monthly:
        rate = rate / cast(Decimal, Decimal('12'))
    
    return cast(Decimal, current_supply * (rate / cast(Decimal, Decimal('100'))))

def calculate_burn(
    current_supply: Decimal,
    config: Optional[BurnConfig],
    period: int
) -> Decimal:
    """Calculate burn amount for a given period."""
    if not config:
        return cast(Decimal, Decimal('0'))
        
    if config.type == "continuous":
        rate = to_decimal(config.rate)
        return cast(Decimal, current_supply * (rate / cast(Decimal, Decimal('100'))))
    else:  # event-based
        if not config.events:
            return cast(Decimal, Decimal('0'))
        return cast(Decimal, sum(
            to_decimal(event.amount) for event in config.events
            if event.period == period
        ))

def calculate_vesting(
    config: VestingConfig,
    period: int
) -> Decimal:
    """Calculate vesting amount for a given period."""
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
                # Release cliff amount
                total_vested += (
                    vest.amount * 
                    Decimal(str(vest.cliff_duration)) / 
                    Decimal(str(vest.duration))
                )
            else:
                # Linear release after cliff
                remaining_periods = vest.duration - vest.cliff_duration
                if remaining_periods > 0:
                    monthly_amount = (
                        vest.amount * 
                        (1 - Decimal(str(vest.cliff_duration)) / Decimal(str(vest.duration))) /
                        Decimal(str(remaining_periods))
                    )
                    total_vested += monthly_amount
        else:  # exponential
            if periods_since_start == vest.cliff_duration:
                # Release cliff amount
                total_vested += vest.amount * Decimal('0.25')
            else:
                # Exponential release after cliff
                remaining_periods = vest.duration - vest.cliff_duration
                if remaining_periods > 0:
                    progress = (periods_since_start - vest.cliff_duration) / remaining_periods
                    total_vested += vest.amount * Decimal('0.75') * (
                        Decimal(str(progress)) ** Decimal('0.5')
                    )
    
    return total_vested

def calculate_staking(
    config: StakingConfig,
    current_supply: Decimal,
    current_staked: Decimal,
    period: int,
    is_monthly: bool
) -> tuple[Decimal, Decimal]:
    """Calculate staking changes and rewards."""
    if not config.enabled:
        return Decimal('0'), Decimal('0')
    
    # Convert annual rate to monthly if needed
    reward_rate = config.reward_rate / (Decimal('12') if is_monthly else Decimal('1'))
    
    # Calculate rewards
    rewards = current_staked * (reward_rate / Decimal('100'))
    
    # Calculate target staked amount
    target_staked = current_supply * (config.target_rate / Decimal('100'))
    
    # Adjust staking based on target
    if current_staked < target_staked:
        available_for_staking = current_supply - current_staked
        staking_increase = min(
            (target_staked - current_staked) * Decimal('0.1'),  # 10% monthly progress toward target
            available_for_staking
        )
        current_staked += staking_increase
    
    # Handle unstaking after lock period
    if period > config.lock_duration:
        unstaking = current_staked * Decimal('0.1')  # 10% monthly unstaking
        current_staked -= unstaking
    
    return current_staked, rewards

def simulate_scenario(request: ScenarioRequest) -> List[TokenPoint]:
    """Simulate a complete token scenario with inflation, burn, vesting, and staking."""
    simulation_data = []
    total_supply = request.initial_supply
    circulating_supply = request.initial_supply
    total_burned = Decimal('0')
    total_rewards = Decimal('0')
    staked_supply = Decimal('0')
    
    # Initialize burn configuration
    burn_rate = request.burn_rate if request.burn_rate is not None else Decimal('0')
    burn_events = request.burn_events if request.burn_events is not None else []
    
    # Initialize staking configuration
    staking_rate = request.staking_rate if request.staking_rate is not None else Decimal('0')
    staking_reward_rate = request.staking_reward_rate if request.staking_reward_rate is not None else Decimal('0')
    staking_lock_period = request.staking_lock_period if request.staking_lock_period is not None else 0
    
    # Initialize vesting configuration
    vesting_periods = request.vesting_periods if request.vesting_periods is not None else []
    
    # Calculate vesting schedule
    vesting_schedule = [Decimal('0')] * (request.duration + 1)
    for period in vesting_periods:
        cliff_month = period.start_month + period.cliff_months
        remaining_months = period.duration_months - period.cliff_months
        
        if remaining_months > 0:
            monthly_amount = period.tokens_amount / Decimal(str(period.duration_months))
            if period.cliff_months > 0 and cliff_month <= request.duration:
                vesting_schedule[cliff_month] += monthly_amount * Decimal(str(period.cliff_months))
            for month in range(cliff_month + 1, min(period.start_month + period.duration_months + 1, request.duration + 1)):
                vesting_schedule[month] += monthly_amount
        else:
            if cliff_month <= request.duration:
                vesting_schedule[cliff_month] += period.tokens_amount
    
    # Calculate target staked amount
    target_staked = total_supply * (staking_rate / Decimal('100'))
    monthly_staking_growth = Decimal('0.20')  # 20% monthly growth towards target
    monthly_reward_rate = staking_reward_rate / Decimal('12')
    
    # Simulate month by month
    for month in range(request.duration + 1):
        # Apply inflation if configured
        if request.inflation_rate is not None and month > 0:
            inflation_amount = total_supply * (request.inflation_rate / Decimal('1200'))  # Convert annual rate to monthly
            total_supply += inflation_amount
            circulating_supply += inflation_amount
        
        # Apply burn rate
        if month > 0:
            # Continuous burn
            if burn_rate > 0:
                burn_amount = circulating_supply * (burn_rate / Decimal('1200'))  # Convert annual rate to monthly
                total_burned += burn_amount
                total_supply -= burn_amount
                circulating_supply -= burn_amount
            
            # Event-based burns
            for event in burn_events:
                if event.month == month:
                    total_burned += event.amount
                    total_supply -= event.amount
                    circulating_supply -= event.amount
            
            # Apply vesting
            vested_amount = vesting_schedule[month]
            circulating_supply += vested_amount
            
            # Calculate and distribute staking rewards
            if staking_rate > 0:
                monthly_rewards = staked_supply * (monthly_reward_rate / Decimal('100'))
                total_rewards += monthly_rewards
                total_supply += monthly_rewards
                circulating_supply += monthly_rewards
                
                # Adjust staking based on target
                if staked_supply < target_staked:
                    available_for_staking = circulating_supply - staked_supply
                    gap_to_target = target_staked - staked_supply
                    staking_increase = min(
                        gap_to_target * monthly_staking_growth,
                        available_for_staking * monthly_staking_growth,
                        gap_to_target
                    )
                    staked_supply += staking_increase
                    circulating_supply -= staking_increase
                
                # Handle unstaking after lock period
                if month > staking_lock_period:
                    excess_staked = max(Decimal('0'), staked_supply - target_staked)
                    if excess_staked > 0:
                        unstaking_rate = Decimal('0.05')
                        unstaking_amount = min(
                            excess_staked * unstaking_rate,
                            staked_supply - (target_staked * Decimal('0.98'))
                        )
                        staked_supply = max(
                            staked_supply - unstaking_amount,
                            target_staked * Decimal('0.98')
                        )
                        circulating_supply += unstaking_amount
        
        # Record simulation data
        simulation_data.append(TokenPoint(
            month=month,
            total_supply=total_supply.quantize(Decimal('0.00')),
            circulating_supply=circulating_supply.quantize(Decimal('0.00')),
            burned_supply=total_burned.quantize(Decimal('0.00')),
            staked_supply=staked_supply.quantize(Decimal('0.00')),
            rewards_distributed=total_rewards.quantize(Decimal('0.00'))
        ))
    
    return simulation_data 