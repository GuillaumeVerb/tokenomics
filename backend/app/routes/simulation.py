from fastapi import APIRouter, HTTPException
from app.models.tokenomics import (
    InflationSimulationRequest,
    InflationSimulationResponse
)
from app.services.simulation_service import (
    calculate_constant_inflation,
    calculate_supply_increase
)

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post(
    "/constant_inflation",
    response_model=InflationSimulationResponse,
    summary="Simulate constant inflation",
    description="""
    Simulates token supply evolution with a constant inflation rate over a specified period.
    
    The simulation:
    - Starts with the initial supply
    - Applies the same inflation rate each year
    - Returns supply values for each year
    
    Example:
    ```
    {
        "initial_supply": 1000000,
        "inflation_rate": 5,
        "duration_in_years": 10
    }
    ```
    """
)
async def simulate_constant_inflation(
    request: InflationSimulationRequest
) -> InflationSimulationResponse:
    try:
        # Calculate supply evolution
        simulation_data = calculate_constant_inflation(
            request.initial_supply,
            request.inflation_rate,
            request.duration_in_years
        )
        
        # Calculate total increases
        total_increase, percentage_increase = calculate_supply_increase(simulation_data)
        
        return InflationSimulationResponse(
            simulation_data=simulation_data,
            total_supply_increase=total_increase,
            total_supply_increase_percentage=percentage_increase
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in simulation calculation: {str(e)}"
        ) 