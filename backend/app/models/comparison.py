from typing import List, Optional
from pydantic import Field
from decimal import Decimal
import plotly.graph_objects as go
from .base import BaseTokenomicsModel
from .tokenomics import ScenarioRequest

from .scenario import (
    ScenarioResponse, 
    PeriodMetrics, ScenarioSummary
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
        description="List of scenarios to compare (2-5 scenarios)"
    )
    return_combined_graph: bool = Field(
        False,
        description="Whether to return a combined graph of all scenarios"
    )
    metrics_to_graph: Optional[List[str]] = Field(
        None,
        description="List of metrics to include in the graph (e.g., ['circulating_supply', 'staked_supply'])"
    )

class ScenarioComparison(BaseTokenomicsModel):
    """Comparison results for a single scenario."""
    name: str = Field(..., description="Name of the scenario")
    timeline_metrics: List[dict] = Field(..., description="Timeline metrics for the scenario")
    summary_metrics: dict = Field(..., description="Summary metrics for the scenario")

class ComparisonSummary(BaseTokenomicsModel):
    """Summary of ranges for various metrics across all scenarios."""
    supply_range: tuple[float, float] = Field(..., description="Range of total supply values")
    minted_range: tuple[float, float] = Field(..., description="Range of total minted tokens")
    burned_range: tuple[float, float] = Field(..., description="Range of total burned tokens")
    staked_range: tuple[float, float] = Field(..., description="Range of total staked tokens")

class PlotlyGraph(BaseTokenomicsModel):
    """Plotly graph data and layout."""
    data: List[dict] = Field(..., description="Graph data in Plotly format")
    layout: dict = Field(..., description="Graph layout in Plotly format")

class ComparisonResponse(BaseTokenomicsModel):
    """Response model for scenario comparison."""
    scenarios: List[ScenarioComparison] = Field(..., description="Results for each scenario")
    summary: ComparisonSummary = Field(..., description="Summary of ranges across all scenarios")
    combined_graph: Optional[PlotlyGraph] = Field(None, description="Combined graph of all scenarios") 