import pytest
from decimal import Decimal
from app.models.tokenomics import (
    BurnRequest, VestingRequest, StakingRequest,
    BurnEvent, VestingPeriod, VestingConfig, StakingConfig
)
from app.services.token_simulation_service import (
    simulate_burn, simulate_vesting, simulate_staking
)

def test_continuous_burn():
    """Test continuous burn rate simulation"""
    request = BurnRequest(
        initial_supply=Decimal('1000000'),
        duration_in_months=12,
        burn_rate=Decimal('1')  # 1% monthly burn
    )
    
    result = simulate_burn(request)
    
    assert len(result) == 13  # 0 to 12 months
    assert result[0].circulating_supply == Decimal('1000000.00')
    # After 12 months with 1% monthly burn, supply should be around 887,000
    assert Decimal('886000') < result[-1].circulating_supply < Decimal('888000')

def test_burn_events():
    """Test specific burn events simulation"""
    request = BurnRequest(
        initial_supply=Decimal('1000000'),
        duration_in_months=12,
        burn_events=[
            BurnEvent(month=6, amount=Decimal('100000')),
            BurnEvent(month=12, amount=Decimal('50000'))
        ]
    )
    
    result = simulate_burn(request)
    
    assert len(result) == 13
    assert result[6].burned_supply == Decimal('100000.00')
    assert result[-1].burned_supply == Decimal('150000.00')

def test_combined_burn():
    """Test multiple burn events simulation"""
    request = BurnRequest(
        initial_supply=Decimal('1000000'),
        duration_in_months=12,
        burn_events=[
            BurnEvent(month=3, amount=Decimal('5000')),
            BurnEvent(month=6, amount=Decimal('50000')),
            BurnEvent(month=9, amount=Decimal('10000'))
        ]
    )
    
    result = simulate_burn(request)
    
    assert len(result) == 13
    # Verify burn events are applied correctly
    assert result[3].burned_supply == Decimal('5000.00')
    assert result[6].burned_supply == Decimal('55000.00')
    assert result[9].burned_supply == Decimal('65000.00')
    assert result[-1].burned_supply == Decimal('65000.00')

def test_linear_vesting():
    """Test linear vesting simulation."""
    request = VestingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        vesting_config=VestingConfig(
            periods=[
                VestingPeriod(
                    start_period=0,
                    duration=12,
                    amount=Decimal("200000"),
                    cliff_duration=0,
                    release_type="linear"
                )
            ]
        )
    )
    
    timeline = simulate_vesting(request)
    
    # Check initial state
    assert timeline[0].circulating_supply == Decimal("800000")  # initial_supply - vesting_amount
    assert timeline[0].locked_supply == Decimal("200000")  # vesting_amount
    
    # Check monthly vesting
    monthly_vesting = Decimal("200000") / Decimal("12")
    for i in range(1, 13):
        assert timeline[i].locked_supply == Decimal("200000") - (monthly_vesting * i)
        assert timeline[i].circulating_supply == Decimal("800000") + (monthly_vesting * i)

def test_vesting_with_cliff():
    """Test vesting with cliff period."""
    request = VestingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        vesting_config=VestingConfig(
            periods=[
                VestingPeriod(
                    start_period=0,
                    duration=12,
                    amount=Decimal("200000"),
                    cliff_duration=3,
                    release_type="linear"
                )
            ]
        )
    )
    
    timeline = simulate_vesting(request)
    
    # Check cliff period
    for i in range(3):
        assert timeline[i].locked_supply == Decimal("200000")
        assert timeline[i].circulating_supply == Decimal("800000")
    
    # Check vesting after cliff
    monthly_vesting = Decimal("200000") / Decimal("12")
    for i in range(3, 13):
        assert timeline[i].locked_supply == Decimal("200000") - (monthly_vesting * (i - 2))
        assert timeline[i].circulating_supply == Decimal("800000") + (monthly_vesting * (i - 2))

def test_multiple_vesting_periods():
    """Test multiple vesting periods with different schedules."""
    request = VestingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        vesting_config=VestingConfig(
            periods=[
                VestingPeriod(
                    start_period=0,
                    duration=6,
                    amount=Decimal("100000"),
                    cliff_duration=0,
                    release_type="linear"
                ),
                VestingPeriod(
                    start_period=3,
                    duration=6,
                    amount=Decimal("100000"),
                    cliff_duration=0,
                    release_type="linear"
                )
            ]
        )
    )
    
    timeline = simulate_vesting(request)
    
    # Check initial state
    assert timeline[0].locked_supply == Decimal("200000")
    assert timeline[0].circulating_supply == Decimal("800000")
    
    # First period starts immediately
    assert timeline[1].locked_supply < Decimal("200000")
    assert timeline[1].circulating_supply > Decimal("800000")
    
    # Second period starts at month 3
    assert timeline[4].locked_supply < timeline[3].locked_supply

def test_staking_rewards():
    """Test staking rewards distribution."""
    request = StakingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        staking_config=StakingConfig(
            enabled=True,
            target_rate=Decimal("30.0"),
            reward_rate=Decimal("12.0"),
            lock_duration=3
        )
    )
    
    timeline = simulate_staking(request)
    
    # Check initial staking
    assert timeline[0].staked_supply == Decimal("300000")  # 30% of initial supply
    assert timeline[0].rewards_distributed == Decimal("0")
    
    # Check rewards distribution
    for i in range(1, 13):
        assert timeline[i].rewards_distributed > timeline[i-1].rewards_distributed
        assert timeline[i].staked_supply >= Decimal("300000")  # Should never go below target

def test_staking_with_lock():
    """Test staking with lock period."""
    request = StakingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        staking_config=StakingConfig(
            enabled=True,
            target_rate=Decimal("30"),
            reward_rate=Decimal("12"),
            lock_duration=6
        )
    )
    
    timeline = simulate_staking(request)
    assert len(timeline) == 13
    
    # Check locked amount
    assert timeline[0].locked_supply == Decimal("300000")  # 30% of initial supply
    
    # Check unlocking after lock period
    assert timeline[6].locked_supply < Decimal("300000")

def test_invalid_burn_request():
    """Test validation of burn request"""
    with pytest.raises(ValueError):
        BurnRequest(
            initial_supply=Decimal('1000000'),
            duration_in_months=12
            # Missing both burn_rate and burn_events
        )

def test_invalid_vesting_period():
    """Test validation of vesting period"""
    with pytest.raises(ValueError):
        VestingRequest(
            total_supply=Decimal('1000000'),
            duration_in_months=24,
            vesting_periods=[]  # Empty vesting periods
        )

def test_invalid_staking_rate():
    """Test validation of staking rate"""
    with pytest.raises(ValueError):
        StakingRequest(
            total_supply=Decimal('1000000'),
            duration_in_months=12,
            staking_rate=Decimal('150'),  # Invalid rate > 100%
            staking_reward_rate=Decimal('12'),
            lock_period=3
        ) 