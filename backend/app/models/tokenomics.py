from pydantic import BaseModel, Field, validator
from typing import List
from decimal import Decimal

class InflationSimulationRequest(BaseModel):
    initial_supply: Decimal = Field(..., gt=0, description="Initial token supply")
    inflation_rate: Decimal = Field(..., ge=0, le=100, description="Annual inflation rate (percentage)")
    duration_in_years: int = Field(..., gt=0, le=100, description="Duration of simulation in years")
    
    @validator('inflation_rate')
    def validate_inflation_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Inflation rate must be between 0 and 100')
        return v

class SupplyPoint(BaseModel):
    year: int = Field(..., description="Year of simulation (0 = initial)")
    supply: Decimal = Field(..., description="Token supply at given year")

class InflationSimulationResponse(BaseModel):
    simulation_data: List[SupplyPoint]
    total_supply_increase: Decimal
    total_supply_increase_percentage: Decimal 