from pydantic import Field, validator
from typing import List, Optional, Literal, Dict
from decimal import Decimal
from datetime import datetime
from .base import BaseTokenomicsModel
from .tokenomics import (
    InflationConfig, BurnConfig, VestingConfig, StakingConfig,
    VestingPeriod, PeriodMetrics, ScenarioSummary, ComparisonSummary,
    ScenarioRequest
)

class NamedScenarioRequest(ScenarioRequest):
    """Named scenario request model."""
    name: str = Field(..., description="Name of the scenario")

class ScenarioComparison(BaseTokenomicsModel):
    """Comparison between two scenarios."""
    name: str = Field(..., description="Name of the scenario")
    timeline: List[PeriodMetrics] = Field(..., description="Timeline of metrics")
    summary: Dict[str, Decimal] = Field(..., description="Summary metrics") 