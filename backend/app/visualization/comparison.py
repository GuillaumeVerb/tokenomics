"""
Visualization utilities for comparing predictions.
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import plotly.graph_objects as go

from ..models.prediction import PredictionPoint, TimeSeriesPoint


def plot_predictions_comparison(
    scenarios: List[Dict[str, Any]],
    title: str = "Supply Predictions Comparison",
    colors: List[str] = ["#3498db", "#e74c3c"],
    height: int = 700,
    template: str = "plotly_white",
) -> Dict[str, Any]:
    """
    Create an interactive plot comparing multiple prediction scenarios.

    Args:
        scenarios: List of dictionaries containing:
            - name: Scenario name
            - historical_data: List of TimeSeriesPoint
            - prediction: List of PredictionPoint
            - metrics: Dict of metrics
        title: Plot title
        colors: List of colors for different scenarios
        height: Plot height in pixels
        template: Plotly template name

    Returns:
        dict: Plotly figure as a dictionary, ready to be serialized to JSON
    """
    fig = go.Figure()

    # Plot each scenario
    for i, scenario in enumerate(scenarios):
        # Historical data
        historical_dates = [point.date for point in scenario["historical_data"]]
        historical_values = [
            float(point.value) for point in scenario["historical_data"]
        ]

        # Prediction data
        pred_dates = [point.date for point in scenario["prediction"]]
        pred_values = [point.value for point in scenario["prediction"]]
        lower_bounds = [point.lower_bound for point in scenario["prediction"]]
        upper_bounds = [point.upper_bound for point in scenario["prediction"]]

        # Add historical line
        fig.add_trace(
            go.Scatter(
                x=historical_dates,
                y=historical_values,
                mode="lines",
                name=f'{scenario["name"]} (Historical)',
                line=dict(color=colors[i], width=2),
                hovertemplate="Date: %{x}<br>Supply: %{y:,.0f}<extra></extra>",
            )
        )

        # Add prediction with confidence interval
        fig.add_trace(
            go.Scatter(
                x=pred_dates + pred_dates[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill="toself",
                fillcolor=f'rgba{tuple(list(int(colors[i].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=False,
                name=f'{scenario["name"]} Confidence',
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pred_dates,
                y=pred_values,
                mode="lines",
                name=f'{scenario["name"]} (Predicted)',
                line=dict(color=colors[i], width=2, dash="dash"),
                hovertemplate="Date: %{x}<br>Predicted: %{y:,.0f}<extra></extra>",
            )
        )

    # Calculate and plot difference between scenarios if there are exactly 2
    if len(scenarios) == 2:
        # Find overlapping prediction dates
        dates_1 = set(point.date for point in scenarios[0]["prediction"])
        dates_2 = set(point.date for point in scenarios[1]["prediction"])
        common_dates = sorted(list(dates_1.intersection(dates_2)))

        if common_dates:
            # Get values for common dates
            values_1 = {point.date: point.value for point in scenarios[0]["prediction"]}
            values_2 = {point.date: point.value for point in scenarios[1]["prediction"]}

            differences = [values_1[date] - values_2[date] for date in common_dates]

            # Add difference plot
            fig.add_trace(
                go.Scatter(
                    x=common_dates,
                    y=differences,
                    mode="lines",
                    name="Difference",
                    line=dict(color="#2ecc71", width=1),
                    yaxis="y2",
                    hovertemplate="Date: %{x}<br>Difference: %{y:,.0f}<extra></extra>",
                )
            )

            # Add secondary y-axis for differences
            fig.update_layout(
                yaxis2=dict(
                    title="Difference", overlaying="y", side="right", showgrid=False
                )
            )

    # Update layout
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis=dict(title="Date", gridcolor="rgba(0,0,0,0.1)", showgrid=True),
        yaxis=dict(
            title="Supply", gridcolor="rgba(0,0,0,0.1)", showgrid=True, tickformat=",d"
        ),
        hovermode="x unified",
        height=height,
        template=template,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    # Add comparison metrics
    if len(scenarios) == 2:
        metrics_text = (
            f"Comparison Metrics:<br>"
            f"Scenario 1 RMSE: {scenarios[0]['metrics']['rmse']:.2f}<br>"
            f"Scenario 2 RMSE: {scenarios[1]['metrics']['rmse']:.2f}<br>"
            f"Mean Difference: {np.mean(differences):.2f}<br>"
            f"Max Difference: {np.max(np.abs(differences)):.2f}"
        )

        fig.add_annotation(
            text=metrics_text,
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.98,
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
        )

    # Add buttons for various interactions
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Reset Zoom",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range": [
                                    min(
                                        min(historical_dates) for scenario in scenarios
                                    ),
                                    max(max(pred_dates) for scenario in scenarios),
                                ]
                            }
                        ],
                    )
                ],
                x=0.05,
                y=1.1,
                xanchor="left",
                yanchor="top",
            )
        ]
    )

    return fig.to_dict()
