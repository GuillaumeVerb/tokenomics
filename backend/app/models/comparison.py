from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import plotly.graph_objects as go
from pydantic import BaseModel, Field

from .base import BaseTokenomicsModel
from .tokenomics import (
    PeriodMetrics,
    ScenarioRequest,
    ScenarioResponse,
    ScenarioSummary,
)


class NamedScenarioRequest(ScenarioRequest):
    """A scenario request with a name for comparison purposes."""

    name: str = Field(..., description="Name of the scenario for comparison")


class ComparisonRequest(BaseTokenomicsModel):
    """Request model for comparing multiple tokenomics scenarios."""

    scenarios: List[NamedScenarioRequest] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of scenarios to compare (2-5 scenarios)",
    )
    return_combined_graph: bool = Field(
        False, description="Whether to return a combined graph of all scenarios"
    )
    metrics_to_graph: Optional[List[str]] = Field(
        None,
        description="List of metrics to include in the graph (e.g., ['circulating_supply', 'staked_supply'])",
    )


class ScenarioComparison(BaseTokenomicsModel):
    """Comparison results for a single scenario."""

    name: str = Field(..., description="Name of the scenario")
    timeline: List[PeriodMetrics] = Field(
        ..., description="Timeline metrics for the scenario"
    )
    summary: Dict[str, Decimal] = Field(
        ..., description="Summary metrics for the scenario"
    )


class ComparisonSummary(BaseTokenomicsModel):
    """Summary of ranges for various metrics across all scenarios."""

    supply_range: Tuple[float, float] = Field(
        ..., description="Range of total supply values"
    )
    minted_range: Tuple[float, float] = Field(
        ..., description="Range of total minted tokens"
    )
    burned_range: Tuple[float, float] = Field(
        ..., description="Range of total burned tokens"
    )
    staked_range: Tuple[float, float] = Field(
        ..., description="Range of total staked tokens"
    )


class PlotlyGraph(BaseTokenomicsModel):
    """Plotly graph data for visualization."""

    data: List[Dict[str, Any]] = Field(..., description="Plotly trace data")
    layout: Dict[str, Any] = Field(..., description="Plotly layout configuration")


class ComparisonResponse(BaseTokenomicsModel):
    """Response model for scenario comparison."""

    scenarios: List[Dict[str, Any]] = Field(
        ..., description="Results for each scenario"
    )
    comparison_summary: ComparisonSummary = Field(
        ..., description="Summary of ranges across all scenarios"
    )
    combined_graph: Optional[PlotlyGraph] = Field(
        None, description="Combined graph of all scenarios"
    )
