from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Optional

from pydantic import Field, validator

from .base import BaseTokenomicsModel
from .tokenomics import (
    BurnConfig,
    ComparisonSummary,
    InflationConfig,
    PeriodMetrics,
    ScenarioRequest,
    ScenarioSummary,
    StakingConfig,
    VestingConfig,
    VestingPeriod,
)


class NamedScenarioRequest(ScenarioRequest):
    """Named scenario request model."""

    name: str = Field(..., description="Name of the scenario")


class ScenarioComparison(BaseTokenomicsModel):
    """Comparison between two scenarios."""

    name: str = Field(..., description="Name of the scenario")
    timeline: List[PeriodMetrics] = Field(..., description="Timeline of metrics")
    summary: Dict[str, Decimal] = Field(..., description="Summary metrics")
