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
    request = BurnSimulationRequest(
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

def test_linear_vesting():
    """Test linear vesting schedule"""
    request = VestingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration_in_months=24,
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

def test_staking_rewards():
    """Test staking rewards calculation"""
    request = StakingSimulationRequest(
        total_supply=Decimal('1000000'),
        duration_in_months=12,
        staking_rate=Decimal('50'),  # 50% staking participation
        staking_reward_rate=Decimal('12'),  # 12% annual rewards
        lock_period=3
    )
    
    result = simulate_staking(request)
    
    assert len(result) == 13
    assert result[0].staked_supply == Decimal('0.00')
    # After 12 months, roughly 50% should be staked
    assert Decimal('450000') < result[-1].staked_supply < Decimal('550000')
    # Should have distributed some rewards
    assert result[-1].rewards_distributed > Decimal('0')

def test_invalid_burn_request():
    """Test validation of burn request"""
    with pytest.raises(ValueError):
        BurnSimulationRequest(
            initial_supply=Decimal('1000000'),
            duration_in_months=12
            # Missing both burn_rate and burn_events
        )

def test_invalid_vesting_period():
    """Test validation of vesting period"""
    with pytest.raises(ValueError):
        VestingSimulationRequest(
            total_supply=Decimal('1000000'),
            duration_in_months=24,
            vesting_periods=[]  # Empty vesting periods
        )

def test_invalid_staking_rate():
    """Test validation of staking rate"""
    with pytest.raises(ValueError):
        StakingSimulationRequest(
            total_supply=Decimal('1000000'),
            duration_in_months=12,
            staking_rate=Decimal('150'),  # Invalid rate > 100%
            staking_reward_rate=Decimal('12'),
            lock_period=3
        ) 