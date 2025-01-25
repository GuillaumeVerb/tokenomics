from fastapi import APIRouter, HTTPException
from app.models.tokenomics import (
    InflationSimulationRequest,
    InflationSimulationResponse,
    BurnSimulationRequest,
    VestingSimulationRequest,
    StakingSimulationRequest,
    SimulationResponse
)
from app.services.simulation_service import (
    calculate_constant_inflation,
    calculate_supply_increase
)
from app.services.token_simulation_service import simulate_burn, simulate_vesting, simulate_staking

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

@router.post(
    "/burn",
    response_model=SimulationResponse,
    summary="Simulate token burning",
    description="""
    Simulates token burning through either:
    - A continuous burn rate applied monthly
    - Specific burn events at defined months
    
    Example:
    ```json
    {
        "initial_supply": 1000000,
        "duration_in_months": 24,
        "burn_rate": 1.5,
        "burn_events": [
            {"month": 6, "amount": 100000},
            {"month": 12, "amount": 50000}
        ]
    }
    ```
    """
)
async def simulate_token_burn(request: BurnSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_burn(request)
        total_burned = simulation_data[-1].burned_supply if simulation_data else None
        return SimulationResponse(
            simulation_data=simulation_data,
            total_burned=total_burned
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/vesting",
    response_model=SimulationResponse,
    summary="Simulate token vesting",
    description="""
    Simulates token vesting schedules with:
    - Multiple vesting periods
    - Cliff periods
    - Linear or custom release schedules
    
    Example:
    ```json
    {
        "total_supply": 1000000,
        "duration_in_months": 36,
        "vesting_periods": [
            {
                "start_month": 0,
                "duration_months": 24,
                "tokens_amount": 400000,
                "cliff_months": 6
            },
            {
                "start_month": 12,
                "duration_months": 12,
                "tokens_amount": 600000,
                "cliff_months": 0
            }
        ]
    }
    ```
    """
)
async def simulate_token_vesting(request: VestingSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_vesting(request)
        total_vested = simulation_data[-1].circulating_supply if simulation_data else None
        return SimulationResponse(
            simulation_data=simulation_data,
            total_vested=total_vested
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/staking",
    response_model=SimulationResponse,
    summary="Simulate token staking",
    description="""
    Simulates token staking mechanism with:
    - Expected staking participation rate
    - Staking rewards
    - Lock periods
    
    Example:
    ```json
    {
        "total_supply": 1000000,
        "duration_in_months": 12,
        "staking_rate": 60,
        "staking_reward_rate": 12.5,
        "lock_period": 3
    }
    ```
    """
)
async def simulate_token_staking(request: StakingSimulationRequest) -> SimulationResponse:
    try:
        simulation_data = simulate_staking(request)
        final_data = simulation_data[-1]
        return SimulationResponse(
            simulation_data=simulation_data,
            total_staked=final_data.staked_supply,
            total_rewards=final_data.rewards_distributed
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 