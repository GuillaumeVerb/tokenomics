import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.models.comparison import ComparisonRequest, NamedScenarioRequest

client = TestClient(app)

def test_compare_scenarios():
    """Test basic scenario comparison functionality."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config={
                    "type": "constant",
                    "initial_rate": Decimal("5.0")
                }
            ),
            NamedScenarioRequest(
                name="Scenario B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config={
                    "type": "constant",
                    "initial_rate": Decimal("10.0")
                }
            )
        ],
        return_combined_graph=False
    )
    
    response = client.post("/simulate/compare", json=request.dict())
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["scenarios"]) == 2
    assert data["scenarios"][0]["name"] == "Scenario A"
    assert data["scenarios"][1]["name"] == "Scenario B"
    assert "comparison_summary" in data
    assert data["combined_graph"] is None

def test_compare_scenarios_with_graph():
    """Test scenario comparison with Plotly graph generation."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config={
                    "type": "constant",
                    "initial_rate": Decimal("5.0")
                }
            ),
            NamedScenarioRequest(
                name="Scenario B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config={
                    "type": "constant",
                    "initial_rate": Decimal("10.0")
                }
            )
        ],
        return_combined_graph=True,
        metrics_to_graph=["total_supply", "circulating_supply"]
    )
    
    response = client.post("/simulate/compare", json=request.dict())
    assert response.status_code == 200
    
    data = response.json()
    assert data["combined_graph"] is not None
    assert "data" in data["combined_graph"]
    assert "layout" in data["combined_graph"]
    assert len(data["combined_graph"]["data"]) == 4  # 2 metrics × 2 scenarios

def test_compare_scenarios_validation():
    """Test input validation for scenario comparison."""
    # Test minimum number of scenarios
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Scenario A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12
            )
        ],
        return_combined_graph=False
    )
    
    with pytest.raises(ValueError):
        response = client.post("/simulate/compare", json=request.dict())
    
    # Test maximum number of scenarios
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name=f"Scenario {i}",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12
            )
            for i in range(6)
        ],
        return_combined_graph=False
    )
    
    with pytest.raises(ValueError):
        response = client.post("/simulate/compare", json=request.dict())

def test_compare_complex_scenarios():
    """Test comparison of scenarios with multiple mechanisms."""
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Complex A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=24,
                inflation_config={
                    "type": "dynamic",
                    "initial_rate": Decimal("5.0"),
                    "min_rate": Decimal("2.0"),
                    "decay_rate": Decimal("20.0")
                },
                burn_config={
                    "type": "continuous",
                    "rate": Decimal("1.0")
                },
                staking_config={
                    "enabled": True,
                    "target_rate": Decimal("30.0"),
                    "reward_rate": Decimal("8.0"),
                    "lock_duration": 3
                }
            ),
            NamedScenarioRequest(
                name="Complex B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=24,
                inflation_config={
                    "type": "halving",
                    "initial_rate": Decimal("8.0"),
                    "halving_period": 12
                },
                vesting_config={
                    "periods": [
                        {
                            "start_period": 0,
                            "duration": 12,
                            "amount": Decimal("200000"),
                            "cliff_duration": 3,
                            "release_type": "linear"
                        }
                    ]
                }
            )
        ],
        return_combined_graph=True
    )
    
    response = client.post("/simulate/compare", json=request.dict())
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["scenarios"]) == 2
    
    # Check that complex mechanisms are properly simulated
    scenario_a = data["scenarios"][0]
    assert any(m["burned_amount"] > 0 for m in scenario_a["timeline"])
    assert any(m["staked_amount"] > 0 for m in scenario_a["timeline"])
    
    scenario_b = data["scenarios"][1]
    assert any(m["vested_amount"] > 0 for m in scenario_b["timeline"])
    
    # Check comparison summary
    summary = data["comparison_summary"]
    assert all(key in summary for key in [
        "supply_range",
        "minted_range",
        "burned_range",
        "staked_range",
        "supply_change_range"
    ])

def test_compare_scenarios_error_handling():
    """Test error handling in scenario comparison."""
    # Test invalid duration
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Invalid A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=361  # Exceeds maximum
            ),
            NamedScenarioRequest(
                name="Invalid B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12
            )
        ],
        return_combined_graph=False
    )
    
    response = client.post("/simulate/compare", json=request.dict())
    assert response.status_code == 400
    
    # Test invalid inflation rate
    request = ComparisonRequest(
        scenarios=[
            NamedScenarioRequest(
                name="Invalid A",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12,
                inflation_config={
                    "type": "constant",
                    "initial_rate": Decimal("101.0")  # Exceeds maximum
                }
            ),
            NamedScenarioRequest(
                name="Invalid B",
                initial_supply=Decimal("1000000"),
                time_step="monthly",
                duration=12
            )
        ],
        return_combined_graph=False
    )
    
    response = client.post("/simulate/compare", json=request.dict())
    assert response.status_code == 400 