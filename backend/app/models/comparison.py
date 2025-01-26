from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal
import plotly.graph_objects as go

from .scenario import (
    ScenarioRequest, ScenarioResponse, 
    PeriodMetrics, ScenarioSummary
)

class NamedScenarioRequest(ScenarioRequest):
    name: str = Field(..., description="Unique name for the scenario")

class ComparisonRequest(BaseModel):
    scenarios: List[NamedScenarioRequest] = Field(
        ...,
        min_items=2,
        max_items=5,
        description="List of scenarios to compare (2-5 scenarios)"
    )
    return_combined_graph: bool = Field(
        False,
        description="Whether to return a combined Plotly graph"
    )
    metrics_to_graph: Optional[List[str]] = Field(
        ["total_supply", "circulating_supply", "staked_amount"],
        description="Metrics to include in the combined graph"
    )

class ScenarioComparison(BaseModel):
    name: str = Field(..., description="Scenario name")
    timeline: List[PeriodMetrics] = Field(..., description="Period by period metrics")
    summary: ScenarioSummary = Field(..., description="Scenario summary metrics")

class ComparisonSummary(BaseModel):
    supply_range: Dict[str, Decimal] = Field(
        ..., 
        description="Final supply range across scenarios"
    )
    minted_range: Dict[str, Decimal] = Field(
        ..., 
        description="Total minted range across scenarios"
    )
    burned_range: Dict[str, Decimal] = Field(
        ..., 
        description="Total burned range across scenarios"
    )
    staked_range: Dict[str, Decimal] = Field(
        ..., 
        description="Final staked amount range across scenarios"
    )
    supply_change_range: Dict[str, Decimal] = Field(
        ..., 
        description="Supply change % range across scenarios"
    )

class PlotlyGraph(BaseModel):
    data: List[dict] = Field(..., description="Plotly graph data")
    layout: dict = Field(..., description="Plotly graph layout")

class ComparisonResponse(BaseModel):
    scenarios: List[ScenarioComparison] = Field(
        ..., 
        description="Results for each scenario"
    )
    comparison_summary: ComparisonSummary = Field(
        ..., 
        description="Summary of ranges across scenarios"
    )
    combined_graph: Optional[PlotlyGraph] = Field(
        None,
        description="Combined Plotly graph if requested"
    ) 