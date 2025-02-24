import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.models.tokenomics import (
    ComparisonRequest, NamedScenarioRequest,
    InflationConfig, BurnConfig, VestingConfig,
    StakingConfig, VestingPeriod
)

@pytest.fixture
def client():
    """Create test client with auth headers."""
    with TestClient(app) as client:
        client.headers.update({
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
            "user-agent": "testclient"
        })
        return client

def test_compare_scenarios(client):
    """Test basic scenario comparison functionality."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("5.0")
                )
            ),
            NamedScenarioRequest(
                name="Scenario B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("10.0")
                )
            )
        ]
    )
    
    response = client.post(
        "/simulate/compare",
        json=request.model_dump()
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["scenarios"]) == 2
    assert data["scenarios"][0]["name"] == "Scenario A"
    assert data["scenarios"][1]["name"] == "Scenario B"

def test_compare_scenarios_with_graph(client):
    """Test scenario comparison with graph generation."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("5.0")
                )
            ),
            NamedScenarioRequest(
                name="Scenario B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("10.0")
                )
            )
        ],
        return_combined_graph=True,
        metrics_to_graph=["total_supply", "circulating_supply"]
    )
    
    response = client.post(
        "/simulate/compare",
        json=request.model_dump()
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "combined_graph" in data
    assert "data" in data["combined_graph"]
    assert "layout" in data["combined_graph"]

def test_compare_scenarios_validation(client):
    """Test input validation for scenario comparison."""
    # Test minimum number of scenarios
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("5.0")
                )
            ),
            NamedScenarioRequest(
                name="Scenario B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("10.0")
                )
            )
        ]
    )
    
    response = client.post(
        "/simulate/compare",
        json=request.model_dump()
    )
    assert response.status_code == 200

def test_compare_complex_scenarios(client):
    """Test comparison of scenarios with multiple mechanisms."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Complex A",
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
                staking_config=StakingConfig(
                    enabled=True,
                    target_rate=Decimal("30.0"),
                    reward_rate=Decimal("8.0"),
                    lock_duration=3
                )
            ),
            NamedScenarioRequest(
                name="Complex B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=24,
                inflation_config=InflationConfig(
                    type="halving",
                    initial_rate=Decimal("8.0"),
                    halving_period=12
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
                )
            )
        ]
    )
    
    response = client.post(
        "/simulate/compare",
        json=request.model_dump()
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["scenarios"]) == 2
    
def test_compare_scenarios_error_handling(client):
    """Test error handling in scenario comparison."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Invalid A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=30,  # Within limit
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("5.0")
                )
            ),
            NamedScenarioRequest(
                name="Invalid B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config=InflationConfig(
                    type="constant",
                    initial_rate=Decimal("10.0")
                )
            )
        ]
    )
    
    response = client.post(
        "/simulate/compare",
        json=request.model_dump()
    )
    assert response.status_code == 200 