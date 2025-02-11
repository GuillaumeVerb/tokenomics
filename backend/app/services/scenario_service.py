from decimal import Decimal
from typing import Any, List, Optional, Union, cast

from app.models.tokenomics import (
    BurnConfig,
    InflationConfig,
    PeriodMetrics,
    ScenarioRequest,
    ScenarioResponse,
    ScenarioSummary,
    StakingConfig,
    TokenPoint,
    VestingConfig,
)


def to_decimal(value: Union[int, float, Decimal, None]) -> Decimal:
    """Convert a value to Decimal, returning Decimal('0') for None."""
    if value is None:
        return cast(Decimal, Decimal("0"))
    return cast(Decimal, Decimal(str(value)))


def calculate_inflation(
    current_supply: Decimal, config: InflationConfig, period: int, is_monthly: bool
) -> Decimal:
    """Calculate inflation for a given period."""
    if not config or not config.initial_rate:
        return cast(Decimal, Decimal("0"))

    if config.type == "constant":
        rate = to_decimal(config.initial_rate)
    elif config.type == "halving":
        halving_period = int(config.halving_period or 1)
        halvings = period // (halving_period * (12 if is_monthly else 1))
        rate = to_decimal(config.initial_rate) / cast(
            Decimal, Decimal(str(2**halvings))
        )
    else:  # dynamic
        min_rate = to_decimal(config.min_rate)
        decay_rate = to_decimal(config.decay_rate)
        decay = decay_rate / cast(Decimal, Decimal(str(12 if is_monthly else 1)))
        rate = cast(
            Decimal,
            max(
                min_rate,
                to_decimal(config.initial_rate)
                * (
                    (
                        cast(Decimal, Decimal("1"))
                        - decay / cast(Decimal, Decimal("100"))
                    )
                    ** period
                ),
            ),
        )

    # Convert annual rate to monthly if needed
    if is_monthly:
        rate = rate / cast(Decimal, Decimal("12"))

    return cast(Decimal, current_supply * (rate / cast(Decimal, Decimal("100"))))


def calculate_burn(
    current_supply: Decimal, config: Optional[BurnConfig], period: int
) -> Decimal:
    """Calculate burn amount for a given period."""
    if not config:
        return cast(Decimal, Decimal("0"))

    if config.type == "continuous":
        rate = to_decimal(config.rate)
        return cast(Decimal, current_supply * (rate / cast(Decimal, Decimal("100"))))
    else:  # event-based
        if not config.events:
            return cast(Decimal, Decimal("0"))
        return cast(
            Decimal,
            sum(
                to_decimal(event.amount)
                for event in config.events
                if event.period == period
            ),
        )


def calculate_vesting(config: VestingConfig, period: int) -> Decimal:
    """Calculate vesting amount for a given period."""
    total_vested = Decimal("0")

    for vesting_period in config.periods:
        if period < vesting_period.start_period:
            continue

        months_since_start = period - vesting_period.start_period

        if months_since_start < vesting_period.cliff_duration:
            continue

        if months_since_start >= vesting_period.duration:
            continue

        if vesting_period.release_type == "linear":
            # Calculate monthly vesting amount
            monthly_amount = vesting_period.amount / Decimal(
                str(vesting_period.duration)
            )

            # If just passed cliff, add cliff portion
            if (
                months_since_start == vesting_period.cliff_duration
                and vesting_period.cliff_duration > 0
            ):
                cliff_amount = monthly_amount * Decimal(
                    str(vesting_period.cliff_duration)
                )
                total_vested += cliff_amount
            else:
                total_vested += monthly_amount

    return total_vested


def calculate_staking(
    config: StakingConfig,
    current_supply: Decimal,
    current_staked: Decimal,
    period: int,
    is_monthly: bool,
) -> tuple[Decimal, Decimal]:
    """Calculate staking changes and rewards."""
    if not config.enabled:
        return Decimal("0"), Decimal("0")

    # Convert annual rate to monthly if needed
    reward_rate = config.reward_rate / (Decimal("12") if is_monthly else Decimal("1"))

    # Calculate rewards
    rewards = current_staked * (reward_rate / Decimal("100"))

    # Calculate target staked amount
    target_staked = current_supply * (config.target_rate / Decimal("100"))

    # Adjust staking based on target
    if current_staked < target_staked:
        available_for_staking = current_supply - current_staked
        staking_increase = min(
            (target_staked - current_staked)
            * Decimal("0.1"),  # 10% monthly progress toward target
            available_for_staking,
        )
        current_staked += staking_increase

    # Handle unstaking after lock period
    if period > config.lock_duration:
        unstaking = current_staked * Decimal("0.1")  # 10% monthly unstaking
        current_staked -= unstaking

    return current_staked, rewards


def simulate_scenario(request: ScenarioRequest) -> ScenarioResponse:
    """Simulate a complete token scenario with inflation, burn, vesting, and staking."""
    timeline = []
    simulation_data = []
    total_supply = request.initial_supply
    circulating_supply = request.initial_supply
    total_burned = Decimal("0")
    total_rewards = Decimal("0")
    staked_supply = Decimal("0")
    total_vested = Decimal("0")
    total_minted = Decimal("0")

    # Initialize burn configuration
    burn_rate = request.burn_config.rate if request.burn_config else Decimal("0")

    # Initialize staking configuration
    staking_config = request.staking_config
    target_staking = (
        total_supply * (staking_config.target_rate / Decimal("100"))
        if staking_config
        else Decimal("0")
    )
    monthly_reward_rate = (
        staking_config.reward_rate / Decimal("12") if staking_config else Decimal("0")
    )

    # Simulate month by month
    for month in range(request.duration_in_months + 1):
        # Apply inflation if configured
        if request.inflation_config and month > 0:
            inflation_amount = calculate_inflation(
                total_supply, request.inflation_config, month, True  # is_monthly
            )
            total_supply += inflation_amount
            circulating_supply += inflation_amount
            total_minted += inflation_amount

        # Apply burn rate
        if month > 0 and burn_rate > 0:
            burn_amount = circulating_supply * (
                burn_rate / Decimal("1200")
            )  # Convert annual rate to monthly
            total_burned += burn_amount
            total_supply -= burn_amount
            circulating_supply -= burn_amount

        # Apply vesting
        if request.vesting_config:
            vested_amount = calculate_vesting(request.vesting_config, month)
            circulating_supply += vested_amount
            total_vested += vested_amount

        # Calculate and distribute staking rewards
        if staking_config and staking_config.enabled:
            monthly_rewards = staked_supply * (monthly_reward_rate / Decimal("100"))
            total_rewards += monthly_rewards
            total_supply += monthly_rewards
            circulating_supply += monthly_rewards
            total_minted += monthly_rewards

            # Adjust staking based on target
            target_staking = total_supply * (
                staking_config.target_rate / Decimal("100")
            )
            if staked_supply < target_staking:
                available_for_staking = circulating_supply - staked_supply
                gap_to_target = target_staking - staked_supply
                staking_increase = min(
                    gap_to_target
                    * Decimal("0.20"),  # 20% monthly growth towards target
                    available_for_staking * Decimal("0.20"),
                    gap_to_target,
                )
                staked_supply += staking_increase
                circulating_supply -= staking_increase

            # Handle unstaking after lock period
            if month > staking_config.lock_duration:
                excess_staked = max(Decimal("0"), staked_supply - target_staking)
                if excess_staked > 0:
                    unstaking_rate = Decimal("0.05")  # 5% monthly unstaking rate
                    unstaking_amount = min(
                        excess_staked * unstaking_rate,
                        staked_supply
                        - (target_staking * Decimal("0.98")),  # Allow 2% below target
                    )
                    staked_supply = max(
                        staked_supply - unstaking_amount,
                        target_staking * Decimal("0.98"),
                    )
                    circulating_supply += unstaking_amount

        # Record timeline metrics
        timeline.append(
            PeriodMetrics(
                period=month,
                total_supply=total_supply.quantize(Decimal("0.01")),
                circulating_supply=circulating_supply.quantize(Decimal("0.01")),
                minted_amount=total_minted.quantize(Decimal("0.01")),
                burned_amount=total_burned.quantize(Decimal("0.01")),
                vested_amount=total_vested.quantize(Decimal("0.01")),
                staked_amount=staked_supply.quantize(Decimal("0.01")),
                staking_rewards=total_rewards.quantize(Decimal("0.01")),
                locked_amount=(staked_supply + total_vested).quantize(Decimal("0.01")),
            )
        )

        # Record simulation data
        simulation_data.append(
            TokenPoint(
                month=month,
                total_supply=total_supply.quantize(Decimal("0.01")),
                circulating_supply=circulating_supply.quantize(Decimal("0.01")),
                locked_supply=(staked_supply + total_vested).quantize(Decimal("0.01")),
                burned_supply=total_burned.quantize(Decimal("0.01")),
                staked_supply=staked_supply.quantize(Decimal("0.01")),
                rewards_distributed=total_rewards.quantize(Decimal("0.01")),
            )
        )

    # Calculate summary
    initial_supply = timeline[0].total_supply
    final_supply = timeline[-1].total_supply
    supply_change = final_supply - initial_supply
    supply_change_percentage = (
        supply_change / initial_supply * Decimal("100")
    ).quantize(Decimal("0.01"))

    summary = ScenarioSummary(
        final_supply=final_supply,
        total_minted=total_minted,
        total_burned=total_burned,
        total_vested=total_vested,
        total_staking_rewards=total_rewards,
        current_staked=staked_supply,
        current_locked=staked_supply + total_vested,
        supply_change_percentage=supply_change_percentage,
    )

    return ScenarioResponse(
        timeline=timeline, summary=summary, simulation_data=simulation_data
    )
