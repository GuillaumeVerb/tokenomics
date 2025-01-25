from decimal import Decimal
from typing import List
from app.models.tokenomics import SupplyPoint

def calculate_constant_inflation(
    initial_supply: Decimal,
    inflation_rate: Decimal,
    duration_in_years: int
) -> List[SupplyPoint]:
    """
    Calculate token supply evolution with constant inflation rate.
    
    Args:
        initial_supply: Initial token supply
        inflation_rate: Annual inflation rate (percentage)
        duration_in_years: Duration of simulation in years
        
    Returns:
        List of SupplyPoint containing year and supply for each period
    """
    simulation_data = []
    current_supply = initial_supply
    rate_multiplier = Decimal('1') + (inflation_rate / Decimal('100'))
    
    # Add initial point
    simulation_data.append(SupplyPoint(year=0, supply=current_supply))
    
    # Calculate supply for each year
    for year in range(1, duration_in_years + 1):
        current_supply = current_supply * rate_multiplier
        simulation_data.append(SupplyPoint(
            year=year,
            supply=current_supply.quantize(Decimal('0.00'))
        ))
    
    return simulation_data

def calculate_supply_increase(
    simulation_data: List[SupplyPoint]
) -> tuple[Decimal, Decimal]:
    """
    Calculate total supply increase in absolute and percentage terms.
    """
    if len(simulation_data) < 2:
        return Decimal('0'), Decimal('0')
        
    initial_supply = simulation_data[0].supply
    final_supply = simulation_data[-1].supply
    
    total_increase = final_supply - initial_supply
    percentage_increase = (total_increase / initial_supply * Decimal('100')).quantize(Decimal('0.00'))
    
    return total_increase.quantize(Decimal('0.00')), percentage_increase 