import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.config import settings

client = TestClient(app)

# Fixtures
@pytest.fixture
def auth_headers():
    """Generate valid JWT token for tests."""
    token = jwt.encode(
        {
            "sub": "test@example.com",
            "exp": datetime.utcnow() + timedelta(days=1)
        },
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def invalid_token():
    """Generate expired JWT token."""
    token = jwt.encode(
        {
            "sub": "test@example.com",
            "exp": datetime.utcnow() - timedelta(days=1)
        },
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}

# Test Authentication
def test_endpoint_without_token():
    """Test that endpoints require authentication."""
    response = client.post("/simulate/constant_inflation", json={})
    assert response.status_code == 401

def test_endpoint_with_invalid_token(invalid_token):
    """Test that invalid tokens are rejected."""
    response = client.post(
        "/simulate/constant_inflation",
        headers=invalid_token,
        json={}
    )
    assert response.status_code == 401

# Test Constant Inflation
def test_constant_inflation_simulation(auth_headers):
    """Test basic constant inflation simulation."""
    request_data = {
        "initial_supply": 1000000,
        "inflation_rate": 5.0,
        "duration_in_years": 3
    }
    
    response = client.post(
        "/simulate/constant_inflation",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "simulation_data" in data
    assert len(data["simulation_data"]) == 4  # initial + 3 years
    assert data["simulation_data"][0]["supply"] == 1000000
    assert data["total_supply_increase_percentage"] > 0

def test_constant_inflation_validation(auth_headers):
    """Test input validation for constant inflation."""
    # Test negative inflation rate
    request_data = {
        "initial_supply": 1000000,
        "inflation_rate": -5.0,
        "duration_in_years": 3
    }
    
    response = client.post(
        "/simulate/constant_inflation",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 400

# Test Burn Simulation
def test_continuous_burn_simulation(auth_headers):
    """Test continuous burn simulation."""
    request_data = {
        "initial_supply": 1000000,
        "duration_in_months": 12,
        "burn_rate": 1.0
    }
    
    response = client.post(
        "/simulate/burn",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "simulation_data" in data
    assert len(data["simulation_data"]) == 13  # initial + 12 months
    assert data["total_burned"] > 0

def test_event_based_burn_simulation(auth_headers):
    """Test event-based burn simulation."""
    request_data = {
        "initial_supply": 1000000,
        "duration_in_months": 12,
        "burn_events": [
            {"month": 3, "amount": 50000},
            {"month": 6, "amount": 75000}
        ]
    }
    
    response = client.post(
        "/simulate/burn",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_burned"] == 125000

# Test Vesting Simulation
def test_linear_vesting_simulation(auth_headers):
    """Test linear vesting simulation."""
    request_data = {
        "total_supply": 1000000,
        "duration_in_months": 12,
        "vesting_periods": [
            {
                "start_month": 0,
                "duration_months": 12,
                "tokens_amount": 100000,
                "cliff_months": 3
            }
        ]
    }
    
    response = client.post(
        "/simulate/vesting",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check cliff period
    assert data["simulation_data"][2]["vested"] == 0
    # Check vesting started after cliff
    assert data["simulation_data"][3]["vested"] > 0

# Test Staking Simulation
def test_staking_simulation(auth_headers):
    """Test staking simulation."""
    request_data = {
        "total_supply": 1000000,
        "duration_in_months": 12,
        "staking_rate": 60.0,
        "staking_reward_rate": 12.0,
        "lock_period": 3
    }
    
    response = client.post(
        "/simulate/staking",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_staked"] > 0
    assert data["total_rewards"] > 0

# Test Scenario Simulation
def test_complete_scenario_simulation(auth_headers):
    """Test complete scenario simulation."""
    request_data = {
        "initial_supply": 1000000,
        "time_step": "monthly",
        "duration": 12,
        "inflation_config": {
            "type": "dynamic",
            "initial_rate": 10.0,
            "min_rate": 2.0,
            "decay_rate": 20.0
        },
        "burn_config": {
            "type": "continuous",
            "rate": 1.0
        },
        "staking_config": {
            "enabled": True,
            "target_rate": 40.0,
            "reward_rate": 8.0,
            "lock_duration": 3
        }
    }
    
    response = client.post(
        "/simulate/scenario",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "timeline" in data
    assert "summary" in data
    assert len(data["timeline"]) == 13  # initial + 12 months

# Test Scenario Comparison
def test_scenario_comparison(auth_headers):
    """Test scenario comparison functionality."""
    request_data = {
        "scenarios": [
            {
                "name": "Conservative",
                "initial_supply": 1000000,
                "time_step": "monthly",
                "duration": 12,
                "inflation_config": {
                    "type": "dynamic",
                    "initial_rate": 5.0,
                    "min_rate": 2.0,
                    "decay_rate": 20.0
                }
            },
            {
                "name": "Aggressive",
                "initial_supply": 1000000,
                "time_step": "monthly",
                "duration": 12,
                "inflation_config": {
                    "type": "dynamic",
                    "initial_rate": 10.0,
                    "min_rate": 5.0,
                    "decay_rate": 10.0
                }
            }
        ],
        "return_combined_graph": True
    }
    
    response = client.post(
        "/simulate/compare",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["scenarios"]) == 2
    assert "comparison_summary" in data
    assert "combined_graph" in data

def test_comparison_validation(auth_headers):
    """Test validation for scenario comparison."""
    # Test with single scenario
    request_data = {
        "scenarios": [
            {
                "name": "Single",
                "initial_supply": 1000000,
                "time_step": "monthly",
                "duration": 12
            }
        ]
    }
    
    response = client.post(
        "/simulate/compare",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 400
    
    # Test with too many scenarios
    request_data["scenarios"] = [
        {
            "name": f"Scenario {i}",
            "initial_supply": 1000000,
            "time_step": "monthly",
            "duration": 12
        }
        for i in range(6)
    ]
    
    response = client.post(
        "/simulate/compare",
        headers=auth_headers,
        json=request_data
    )
    
    assert response.status_code == 400 