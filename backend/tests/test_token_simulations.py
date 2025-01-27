import pytest
from decimal import Decimal
from app.models.tokenomics import (
    BurnSimulationRequest, VestingSimulationRequest, StakingSimulationRequest,
    BurnEvent, VestingPeriod
)
from app.services.token_simulation_service import (
    simulate_burn, simulate_vesting, simulate_staking
)

def test_continuous_burn():
    """Test continuous burn rate simulation"""
    request = BurnSimulationRequest(
        initial_supply=Decimal('1000000'),
        duration=12,
        burn_rate=Decimal('1')  # 1% monthly burn
    )
    
    result = simulate_burn(request)
    
    assert len(result) == 13  # 0 to 12 months
    assert result[0].circulating_supply == Decimal('1000000.00')
    # After 12 months with 1% monthly burn, supply should be around 887,000
    assert Decimal('886000') < result[-1].circulating_supply < Decimal('888000')

def test_burn_events():
    """Test specific burn events simulation"""
    request = BurnSimulationRequest(
        initial_supply=Decimal('1000000'),
        duration=12,
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
    request = BurnSimulationRequest(
        initial_supply=Decimal('1000000'),
        duration=12,
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
    """Test linear vesting schedule"""
    request = VestingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration=24,
        vesting_periods=[
            VestingPeriod(
                start_month=0,
                duration_months=12,
                tokens_amount=Decimal('1000000'),
                cliff_months=0
            )
        ]
    )
    
    result = simulate_vesting(request)
    
    assert len(result) == 25  # 0 to 24 months
    assert result[0].circulating_supply == Decimal('0.00')
    assert result[6].circulating_supply == Decimal('500000.00')
    assert result[12].circulating_supply == Decimal('1000000.00')

def test_vesting_with_cliff():
    """Test vesting schedule with cliff period"""
    request = VestingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration=24,
        vesting_periods=[
            VestingPeriod(
                start_month=0,
                duration_months=12,
                tokens_amount=Decimal('1000000'),
                cliff_months=6
            )
        ]
    )
    
    result = simulate_vesting(request)
    
    assert len(result) == 25
    # No tokens released during cliff
    assert all(point.circulating_supply == Decimal('0.00') for point in result[:6])
    # Linear release after cliff
    assert result[9].circulating_supply == Decimal('500000.00')
    assert result[12].circulating_supply == Decimal('1000000.00')

def test_multiple_vesting_periods():
    """Test multiple overlapping vesting periods"""
    request = VestingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration=24,
        vesting_periods=[
            VestingPeriod(
                start_month=0,
                duration_months=12,
                tokens_amount=Decimal('400000'),
                cliff_months=0
            ),
            VestingPeriod(
                start_month=6,
                duration_months=12,
                tokens_amount=Decimal('600000'),
                cliff_months=3
            )
        ]
    )
    
    result = simulate_vesting(request)
    
    assert len(result) == 25
    # First period starts releasing immediately
    assert result[3].circulating_supply == Decimal('100000.00')
    # Second period starts after its cliff
    assert result[9].circulating_supply > Decimal('200000.00')
    # All tokens released by end
    assert result[-1].circulating_supply == Decimal('1000000.00')

def test_staking_rewards():
    """Test staking rewards calculation"""
    request = StakingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration=12,
        staking_rate=Decimal('50'),  # 50% staking participation
        staking_reward_rate=Decimal('12'),  # 12% annual rewards
        lock_period=3
    )
    
    result = simulate_staking(request)
    
    assert len(result) == 13
    assert result[0].staked_supply == Decimal('0.00')
    # After 12 months, roughly 50% should be staked
    assert result[-1].staked_supply is not None
    assert Decimal('450000') < result[-1].staked_supply < Decimal('550000')
    # Should have distributed some rewards
    assert result[-1].rewards_distributed is not None
    assert result[-1].rewards_distributed > Decimal('0')

def test_staking_with_lock():
    """Test staking with lock period"""
    request = StakingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration=12,
        staking_rate=Decimal('60'),
        staking_reward_rate=Decimal('12'),
        lock_period=6
    )
    
    result = simulate_staking(request)
    
    assert len(result) == 13
    # No unstaking possible before lock period
    for i in range(6):
        current = result[i].staked_supply
        if i > 0:
            previous = result[i-1].staked_supply
            assert current is not None and previous is not None
            assert current >= previous
    
    # Unstaking possible after lock period
    found_decrease = False
    for i in range(7, 13):
        current = result[i].staked_supply
        previous = result[i-1].staked_supply
        assert current is not None and previous is not None
        if current < previous:
            found_decrease = True
            break
    assert found_decrease, "Expected to find at least one decrease in staked supply after lock period"

def test_invalid_burn_request():
    """Test validation of burn request"""
    with pytest.raises(ValueError):
        BurnSimulationRequest(
            initial_supply=Decimal('1000000'),
            duration=12
            # Missing both burn_rate and burn_events
        )

def test_invalid_vesting_period():
    """Test validation of vesting period"""
    with pytest.raises(ValueError):
        VestingSimulationRequest(
            total_supply=Decimal('1000000'),
            duration=24,
            vesting_periods=[]  # Empty vesting periods
        )

def test_invalid_staking_rate():
    """Test validation of staking rate"""
    with pytest.raises(ValueError):
        StakingSimulationRequest(
            total_supply=Decimal('1000000'),
            duration=12,
            staking_rate=Decimal('150'),  # Invalid rate > 100%
            staking_reward_rate=Decimal('12'),
            lock_period=3
        ) 