from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

router = APIRouter()

class ConstantInflationRequest(BaseModel):
    initial_supply: int = Field(..., gt=0, description="Supply initiale de tokens")
    inflation_rate: float = Field(..., ge=0, le=100, description="Taux d'inflation annuel (%)")
    duration_in_years: int = Field(..., gt=0, le=50, description="Durée de la simulation en années")

class SimulationDataPoint(BaseModel):
    year: int
    supply: int

class ConstantInflationResponse(BaseModel):
    simulation_data: List[SimulationDataPoint]
    total_supply_increase: int
    total_supply_increase_percentage: float

@router.post("/constant_inflation", response_model=ConstantInflationResponse)
async def simulate_constant_inflation(request: ConstantInflationRequest):
    """Simule l'évolution de la supply avec un taux d'inflation constant."""
    simulation_data = []
    current_supply = request.initial_supply
    
    # Initial state
    simulation_data.append(SimulationDataPoint(year=0, supply=current_supply))
    
    # Calculate yearly inflation
    for year in range(1, request.duration_in_years + 1):
        increase = int(current_supply * (request.inflation_rate / 100))
        current_supply += increase
        simulation_data.append(SimulationDataPoint(year=year, supply=current_supply))
    
    total_increase = current_supply - request.initial_supply
    total_increase_percentage = (total_increase / request.initial_supply) * 100
    
    return ConstantInflationResponse(
        simulation_data=simulation_data,
        total_supply_increase=total_increase,
        total_supply_increase_percentage=total_increase_percentage
    ) 