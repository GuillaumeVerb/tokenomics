import pytest
from decimal import Decimal
from app.models.tokenomics import ConstantInflationRequest
from app.services.simulation_service import (
    calculate_constant_inflation,
    calculate_supply_increase
)

def test_zero_inflation():
    """Test that zero inflation rate keeps supply constant"""
    simulation_data = calculate_constant_inflation(
        initial_supply=Decimal('1000000'),
        inflation_rate=Decimal('0'),
        duration_in_years=5
    )
    
    assert len(simulation_data) == 6  # initial year + 5 years
    for point in simulation_data:
        assert point.supply == Decimal('1000000')

def test_simple_inflation():
    """Test inflation calculation with simple values"""
    simulation_data = calculate_constant_inflation(
        initial_supply=Decimal('1000'),
        inflation_rate=Decimal('10'),
        duration_in_years=1
    )
    
    assert len(simulation_data) == 2
    assert simulation_data[0].supply == Decimal('1000')
    assert simulation_data[1].supply == Decimal('1100.00')

def test_compound_inflation():
    """Test compound inflation over multiple years"""
    simulation_data = calculate_constant_inflation(
        initial_supply=Decimal('1000'),
        inflation_rate=Decimal('10'),
        duration_in_years=2
    )
    
    assert len(simulation_data) == 3
    assert simulation_data[0].supply == Decimal('1000')
    assert simulation_data[1].supply == Decimal('1100.00')
    assert simulation_data[2].supply == Decimal('1210.00')

def test_supply_increase_calculation():
    """Test calculation of total supply increase"""
    simulation_data = calculate_constant_inflation(
        initial_supply=Decimal('1000'),
        inflation_rate=Decimal('10'),
        duration_in_years=2
    )
    
    total_increase, percentage_increase = calculate_supply_increase(simulation_data)
    assert total_increase == Decimal('210.00')
    assert percentage_increase == Decimal('21.00')

def test_invalid_input_validation():
    """Test that invalid inputs raise appropriate errors"""
    with pytest.raises(ValueError):
        ConstantInflationRequest(
            initial_supply=Decimal('-1000'),
            inflation_rate=Decimal('10'),
            duration_in_years=5
        )
    
    with pytest.raises(ValueError):
        ConstantInflationRequest(
            initial_supply=Decimal('1000'),
            inflation_rate=Decimal('-10'),
            duration_in_years=5
        )
    
    with pytest.raises(ValueError):
        ConstantInflationRequest(
            initial_supply=Decimal('1000'),
            inflation_rate=Decimal('10'),
            duration_in_years=0
        ) 