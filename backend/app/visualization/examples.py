"""
Examples of using the visualization utilities.
"""

from decimal import Decimal

from .supply import plot_supply_evolution


def example_supply_plot():
    # Example data
    data = [
        {"month": i, "circulating_supply": Decimal(1000000 * (1 + i * 0.1))}
        for i in range(25)
    ]

    # Example 1: Basic plot with default settings
    basic_plot = plot_supply_evolution(data)

    # Example 2: Customized plot with different colors and custom annotations
    custom_plot = plot_supply_evolution(
        data,
        title="Token Supply Growth with Key Events",
        line_color="#3498db",  # Blue line
        annotation_color="#e74c3c",  # Red annotations
        show_percentage_markers=True,
        percentage_markers=[0.3, 0.5, 0.7],  # Show 30%, 50%, and 70% markers
        custom_annotations=[
            {
                "x": 6,
                "y": float(data[6]["circulating_supply"]),
                "text": "Exchange Listing",
                "color": "#2ecc71",  # Green annotation
            },
            {
                "x": 12,
                "y": float(data[12]["circulating_supply"]),
                "text": "Token Burn Event",
                "color": "#e67e22",  # Orange annotation
            },
        ],
        height=700,
        template="plotly_dark",  # Dark theme
    )

    return basic_plot, custom_plot


# Usage in FastAPI endpoint
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/supply-chart")
async def get_supply_chart():
    basic_plot, _ = example_supply_plot()
    return JSONResponse(content=basic_plot)

@router.get("/supply-chart-custom")
async def get_custom_supply_chart():
    _, custom_plot = example_supply_plot()
    return JSONResponse(content=custom_plot)
"""

# Usage in Streamlit
"""
import streamlit as st
import plotly.graph_objects as go

def show_supply_charts():
    basic_plot, custom_plot = example_supply_plot()
    
    st.title("Supply Evolution Charts")
    
    st.subheader("Basic Chart")
    st.plotly_chart(go.Figure(basic_plot), use_container_width=True)
    
    st.subheader("Customized Chart")
    st.plotly_chart(go.Figure(custom_plot), use_container_width=True)
"""
