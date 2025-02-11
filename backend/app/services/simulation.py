from typing import Dict, Any
from decimal import Decimal

from app.models.simulation import SimulationParams


def simulate_tokenomics(
    current_supply: float,
    current_price: float,
    current_liquidity: float,
    params: SimulationParams,
) -> Dict[str, float]:
    """
    Simulate one month of tokenomics evolution.

    Args:
        current_supply: Current token supply
        current_price: Current token price
        current_liquidity: Current liquidity ratio
        params: Simulation parameters

    Returns:
        Dict containing updated supply, price, and liquidity
    """
    # Apply monthly inflation
    new_supply = current_supply * (1 + params.monthly_inflation)

    # Calculate new price based on constant market cap assumption
    new_price = (current_supply * current_price) / new_supply

    # Adjust liquidity based on supply change
    supply_change_ratio = new_supply / current_supply
    new_liquidity = current_liquidity * (2 - supply_change_ratio)
    new_liquidity = max(0.01, min(1.0, new_liquidity))  # Keep between 1% and 100%

    return {
        "supply": new_supply,
        "price": new_price,
        "liquidity": new_liquidity,
    } 