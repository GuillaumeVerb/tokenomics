"""
Supply visualization utilities using Plotly.
"""
from typing import List, Dict, Union, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from decimal import Decimal


def plot_supply_evolution(
    data: List[Dict[str, Union[int, Decimal]]],
    title: str = "Token Supply Evolution",
    line_color: str = "#1f77b4",
    annotation_color: str = "#2ecc71",
    show_percentage_markers: bool = True,
    percentage_markers: List[float] = [0.5, 0.8],  # 50% and 80% markers
    custom_annotations: Optional[List[Dict]] = None,
    height: int = 600,
    template: str = "plotly_white"
) -> Dict:
    """
    Create an interactive plot of token supply evolution with customizable annotations.
    
    Args:
        data: List of dictionaries containing supply data points.
             Each dict should have 'month' and 'circulating_supply' keys.
        title: Plot title
        line_color: Color of the supply line (hex or named color)
        annotation_color: Color of the annotations (hex or named color)
        show_percentage_markers: Whether to show default percentage markers
        percentage_markers: List of percentages (0-1) at which to show markers
        custom_annotations: List of custom annotation dictionaries with keys:
            - x: x-coordinate (month)
            - y: y-coordinate (supply amount)
            - text: annotation text
            - color: (optional) annotation color
        height: Plot height in pixels
        template: Plotly template name (e.g., "plotly_white", "plotly_dark", "seaborn")
    
    Returns:
        dict: Plotly figure as a dictionary, ready to be serialized to JSON
        
    Example:
        >>> data = [
        ...     {"month": 0, "circulating_supply": 1000000},
        ...     {"month": 12, "circulating_supply": 1500000},
        ... ]
        >>> custom_annotations = [
        ...     {
        ...         "x": 6,
        ...         "y": 1250000,
        ...         "text": "Major Release",
        ...         "color": "#e74c3c"
        ...     }
        ... ]
        >>> fig = plot_supply_evolution(
        ...     data,
        ...     title="My Token Supply",
        ...     custom_annotations=custom_annotations
        ... )
    """
    # Convert data to lists for plotting
    months = [d['month'] for d in data]
    supply = [float(d['circulating_supply']) for d in data]
    
    # Create the base figure
    fig = go.Figure()
    
    # Add supply line
    fig.add_trace(
        go.Scatter(
            x=months,
            y=supply,
            mode='lines',
            name='Supply',
            line=dict(color=line_color, width=2),
            hovertemplate="Month: %{x}<br>Supply: %{y:,.0f}<extra></extra>"
        )
    )
    
    # Add percentage markers if requested
    if show_percentage_markers and percentage_markers:
        max_supply = max(supply)
        for percentage in percentage_markers:
            target_supply = max_supply * percentage
            # Find the first month where supply exceeds target
            for i, s in enumerate(supply):
                if s >= target_supply:
                    fig.add_annotation(
                        x=months[i],
                        y=s,
                        text=f"{percentage*100:.0f}% Supply",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor=annotation_color,
                        font=dict(color=annotation_color),
                        align="center",
                        yshift=10
                    )
                    break
    
    # Add custom annotations if provided
    if custom_annotations:
        for annotation in custom_annotations:
            fig.add_annotation(
                x=annotation['x'],
                y=annotation['y'],
                text=annotation['text'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=annotation.get('color', annotation_color),
                font=dict(color=annotation.get('color', annotation_color)),
                align="center",
                yshift=10
            )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Month",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title="Supply",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True,
            tickformat=",d"
        ),
        showlegend=False,
        hovermode='x unified',
        height=height,
        template=template,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white'
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
                        args=[{"xaxis.range": [min(months), max(months)],
                              "yaxis.range": [0, max(supply) * 1.1]}]
                    )
                ],
                x=0.05,
                y=1.1,
                xanchor='left',
                yanchor='top'
            )
        ]
    )
    
    # Enable responsive behavior
    fig.update_layout(
        autosize=True,
        modebar=dict(
            orientation='v',
            bgcolor='rgba(0,0,0,0)'
        )
    )
    
    return fig.to_dict()  # Return as dict for easy JSON serialization 