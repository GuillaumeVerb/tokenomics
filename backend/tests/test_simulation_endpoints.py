import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.core.config import settings
from app.models.tokenomics import (
    ConstantInflationRequest,
    BurnRequest,
    VestingRequest,
    StakingRequest,
    ScenarioRequest,
    VestingPeriod,
    BurnEvent,
    InflationConfig,
    BurnConfig,
    VestingConfig,
    StakingConfig
)

client = TestClient(app)

# Fixtures
@pytest.fixture
def auth_headers():
    """Create authentication headers with a valid JWT token."""
    token = jwt.encode(
        {
            'sub': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def invalid_token():
    """Create an invalid JWT token."""
    token = jwt.encode(
        {
            'sub': 'test@example.com',
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expired token
        },
        'wrong-secret',
        algorithm=settings.JWT_ALGORITHM
    )
    return {'Authorization': f'Bearer {token}'}

# Test Authentication
def test_endpoint_without_token():
    """Test that endpoints require authentication."""
    response = client.post('/simulate/constant_inflation', json={})
    assert response.status_code == 401

def test_endpoint_with_invalid_token(invalid_token):
    """Test that endpoints reject invalid tokens."""
    response = client.post(
        '/simulate/constant_inflation',
        headers=invalid_token,
        json={}
    )
    assert response.status_code == 401

# Test Constant Inflation
def test_constant_inflation_simulation(auth_headers):
    """Test the constant inflation simulation endpoint."""
    request = ConstantInflationRequest(
        initial_supply=1000000,
        inflation_rate=5.0,
        duration_in_years=5
    )
    
    response = client.post(
        '/simulate/constant_inflation',
        headers=auth_headers,
        json=request.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'simulation_data' in data
    assert len(data['simulation_data']) == 6  # Initial + 5 years
    assert Decimal(data['simulation_data'][0]['supply']) == Decimal('1000000')

def test_constant_inflation_validation(auth_headers):
    """Test input validation for constant inflation endpoint."""
    # Test invalid inflation rate
    request = ConstantInflationRequest(
        initial_supply=1000000,
        inflation_rate=150.0,  # Invalid: > 100%
        duration_in_years=5
    )
    response = client.post(
        '/simulate/constant_inflation',
        headers=auth_headers,
        json=request.model_dump()
    )
    assert response.status_code == 422
    
    # Test invalid duration
    request = ConstantInflationRequest(
        initial_supply=1000000,
        inflation_rate=5.0,
        duration_in_years=0  # Invalid: <= 0
    )
    response = client.post(
        '/simulate/constant_inflation',
        headers=auth_headers,
        json=request.model_dump()
    )
    assert response.status_code == 422

# Test Burn Simulation
def test_continuous_burn_simulation(auth_headers):
    """Test the continuous burn simulation endpoint."""
    request = BurnRequest(
        initial_supply=1000000,
        duration_in_months=12,
        burn_rate=1.0
    )
    
    response = client.post(
        '/simulate/burn',
        headers=auth_headers,
        json=request.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data['simulation_data']) == 13
    assert Decimal(data['total_burned']) > Decimal('0')

def test_event_based_burn_simulation(auth_headers):
    """Test the event-based burn simulation endpoint."""
    request = BurnRequest(
        initial_supply=1000000,
        duration_in_months=12,
        burn_events=[
            BurnEvent(month=3, amount=50000),
            BurnEvent(month=6, amount=75000)
        ]
    )
    
    response = client.post(
        '/simulate/burn',
        headers=auth_headers,
        json=request.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data['total_burned']) == Decimal('125000.00')

# Test Vesting Simulation
def test_linear_vesting_simulation(auth_headers):
    """Test the vesting simulation endpoint with linear schedule."""
    request = VestingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=24,
        vesting_config=VestingConfig(
            periods=[
                VestingPeriod(
                    start_period=0,
                    duration=12,
                    amount=Decimal("400000"),
                    cliff_duration=0,
                    release_type="linear"
                ),
                VestingPeriod(
                    start_period=6,
                    duration=12,
                    amount=Decimal("600000"),
                    cliff_duration=3,
                    release_type="linear"
                )
            ]
        )
    )
    
    response = client.post(
        '/simulate/vesting',
        headers=auth_headers,
        json=request.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data['simulation_data']) == 25
    assert Decimal(data['total_vested']) == Decimal('1000000.00')

# Test Staking Simulation
def test_staking_simulation(auth_headers):
    """Test the staking simulation endpoint."""
    request = StakingRequest(
        initial_supply=Decimal("1000000"),
        duration_in_months=12,
        staking_config=StakingConfig(
            enabled=True,
            target_rate=Decimal("50"),
            reward_rate=Decimal("12"),
            lock_duration=3
        )
    )
    
    response = client.post(
        '/simulate/staking',
        headers=auth_headers,
        json=request.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data['simulation_data']) == 13
    assert Decimal(data['total_staked']) > Decimal('0')
    assert Decimal(data['total_rewards']) > Decimal('0')

# Test Scenario Simulation
def test_complete_scenario_simulation(auth_headers):
    """Test a complete scenario with multiple mechanisms."""
    request = ScenarioRequest(
        initial_supply=Decimal("1000000"),
        time_step="monthly",
        duration=24,
        inflation_config=InflationConfig(
            type="dynamic",
            initial_rate=Decimal("5.0"),
            min_rate=Decimal("2.0"),
            decay_rate=Decimal("20.0")
        ),
        burn_config=BurnConfig(
            type="continuous",
            rate=Decimal("1.0")
        ),
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
        ),
        staking_config=StakingConfig(
            enabled=True,
            target_rate=Decimal("40.0"),
            reward_rate=Decimal("12.0"),
            lock_duration=3
        )
    )
    
    response = client.post(
        '/simulate/scenario',
        headers=auth_headers,
        json=request.model_dump_json()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'timeline' in data
    assert 'summary' in data
    assert len(data['timeline']) == 25  # 0 to 24 months
    
    # Verify all mechanisms are working
    summary = data['summary']
    assert Decimal(summary['total_minted']) > Decimal('0')  # Inflation working
    assert Decimal(summary['total_burned']) > Decimal('0')  # Burning working
    assert Decimal(summary['total_vested']) > Decimal('0')  # Vesting working
    assert Decimal(summary['total_staking_rewards']) > Decimal('0')  # Staking working

# Test Scenario Comparison
def test_scenario_comparison(auth_headers):
    """Test comparing multiple scenarios."""
    request_data = {
        'scenarios': [
            {
                'name': 'Conservative',
                'initial_supply': 1000000,
                'time_step': 'monthly',
                'duration': 24,
                'inflation_config': {
                    'type': 'dynamic',
                    'initial_rate': 5.0,
                    'min_rate': 2.0,
                    'decay_rate': 20.0
                }
            },
            {
                'name': 'Aggressive',
                'initial_supply': 1000000,
                'time_step': 'monthly',
                'duration': 24,
                'inflation_config': {
                    'type': 'dynamic',
                    'initial_rate': 10.0,
                    'min_rate': 5.0,
                    'decay_rate': 10.0
                }
            }
        ],
        'return_combined_graph': True
    }
    
    response = client.post(
        '/simulate/compare',
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data['scenarios']) == 2
    assert 'comparison_summary' in data
    assert 'combined_graph' in data
    
    # Verify the aggressive scenario has higher final supply
    conservative_supply = data['scenarios'][0]['summary']['final_supply']
    aggressive_supply = data['scenarios'][1]['summary']['final_supply']
    assert aggressive_supply > conservative_supply

def test_comparison_validation(auth_headers):
    """Test validation for scenario comparison."""
    # Test with too few scenarios
    response = client.post(
        '/simulate/compare',
        headers=auth_headers,
        json={
            'scenarios': [
                {
                    'name': 'Single Scenario',
                    'initial_supply': 1000000,
                    'time_step': 'monthly',
                    'duration': 24
                }
            ]
        }
    )
    assert response.status_code == 422
    
    # Test with too many scenarios
    response = client.post(
        '/simulate/compare',
        headers=auth_headers,
        json={
            'scenarios': [
                {
                    'name': f'Scenario {i}',
                    'initial_supply': 1000000,
                    'time_step': 'monthly',
                    'duration': 24
                }
                for i in range(6)  # Max is 5
            ]
        }
    )
    assert response.status_code == 422 