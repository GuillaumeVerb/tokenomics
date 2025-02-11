"""
Visualization utilities for supply predictions.
"""

from datetime import datetime
from typing import Any, Dict, List

import plotly.graph_objects as go

from ..models.prediction import PredictionPoint, TimeSeriesPoint


def plot_prediction(
    historical_data: List[TimeSeriesPoint],
    prediction: List[PredictionPoint],
    title: str = "Supply Prediction",
    historical_color: str = "#1f77b4",
    prediction_color: str = "#2ecc71",
    confidence_color: str = "rgba(46, 204, 113, 0.2)",
    height: int = 600,
    template: str = "plotly_white",
) -> Dict[str, Any]:
    """
    Create an interactive plot combining historical data and predictions.

    Args:
        historical_data: List of historical data points
        prediction: List of predicted points with confidence intervals
        title: Plot title
        historical_color: Color for historical data line
        prediction_color: Color for prediction line
        confidence_color: Color for confidence interval area
        height: Plot height in pixels
        template: Plotly template name

    Returns:
        dict: Plotly figure as a dictionary, ready to be serialized to JSON
    """
    fig = go.Figure()

    # Add historical data
    historical_dates = [point.date for point in historical_data]
    historical_values = [float(point.value) for point in historical_data]

    fig.add_trace(
        go.Scatter(
            x=historical_dates,
            y=historical_values,
            mode="lines",
            name="Historical",
            line=dict(color=historical_color, width=2),
            hovertemplate="Date: %{x}<br>Supply: %{y:,.0f}<extra></extra>",
        )
    )

    # Add prediction with confidence interval
    pred_dates = [point.date for point in prediction]
    pred_values = [point.value for point in prediction]
    lower_bounds = [point.lower_bound for point in prediction]
    upper_bounds = [point.upper_bound for point in prediction]

    # Add confidence interval
    fig.add_trace(
        go.Scatter(
            x=pred_dates + pred_dates[::-1],
            y=upper_bounds + lower_bounds[::-1],
            fill="toself",
            fillcolor=confidence_color,
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False,
            name="Confidence Interval",
        )
    )

    # Add prediction line
    fig.add_trace(
        go.Scatter(
            x=pred_dates,
            y=pred_values,
            mode="lines",
            name="Prediction",
            line=dict(color=prediction_color, width=2),
            hovertemplate="Date: %{x}<br>Predicted: %{y:,.0f}<extra></extra>",
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
                                "xaxis.range": [min(historical_dates), max(pred_dates)],
                                "yaxis.range": [
                                    min(lower_bounds + historical_values) * 0.9,
                                    max(upper_bounds + historical_values) * 1.1,
                                ],
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
