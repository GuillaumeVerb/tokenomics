"""
Streamlit page for comparing supply predictions.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def load_data(uploaded_file) -> List[Dict[str, Any]]:
    """Load and validate uploaded JSON data."""
    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        data = json.loads(content)
        
        # Validate data structure
        if not isinstance(data, list):
            st.error("Data must be a list of time series points")
            return None
            
        for point in data:
            if not all(k in point for k in ['date', 'value']):
                st.error("Each point must have 'date' and 'value' fields")
                return None
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def generate_pdf_report(scenarios: List[Dict[str, Any]], fig: go.Figure) -> bytes:
    """Generate PDF report with predictions comparison."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Prepare content
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    elements.append(Paragraph("Supply Predictions Comparison", styles['Title']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # Save plot to temporary buffer
    plot_buffer = io.BytesIO()
    fig.write_image(file=plot_buffer, format='png')
    plot_buffer.seek(0)
    
    # Add plot
    elements.append(Paragraph("Predictions Plot", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Metrics table
    elements.append(Paragraph("Comparison Metrics", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    if len(scenarios) == 2:
        metrics_data = [
            ['Metric', 'Scenario 1', 'Scenario 2'],
            ['RMSE', f"{scenarios[0]['metrics']['rmse']:.2f}", f"{scenarios[1]['metrics']['rmse']:.2f}"],
            ['MAE', f"{scenarios[0]['metrics']['mae']:.2f}", f"{scenarios[1]['metrics']['mae']:.2f}"]
        ]
        
        table = Table(metrics_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.title("Compare Supply Predictions")
    
    # File upload
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload Scenario 1 (JSON)", type=['json'])
    with col2:
        file2 = st.file_uploader("Upload Scenario 2 (JSON)", type=['json'])
    
    # Model parameters
    st.subheader("Model Parameters")
    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox(
            "Model Type",
            options=['prophet', 'arima', 'lstm'],
            index=0
        )
    with col2:
        forecast_years = st.slider(
            "Forecast Years",
            min_value=1,
            max_value=10,
            value=5
        )
    
    if file1 and file2:
        data1 = load_data(file1)
        data2 = load_data(file2)
        
        if data1 and data2:
            # Generate predictions
            if st.button("Generate Predictions", type="primary"):
                with st.spinner("Generating predictions..."):
                    try:
                        # Make API calls
                        scenarios = []
                        for i, data in enumerate([data1, data2]):
                            response = requests.post(
                                "http://localhost:8000/predict",
                                json={
                                    "historical_data": data,
                                    "forecast_years": forecast_years,
                                    "model_type": model_type,
                                    "confidence_interval": 0.95
                                }
                            )
                            response.raise_for_status()
                            scenarios.append({
                                "name": f"Scenario {i+1}",
                                "historical_data": data,
                                "prediction": response.json()
                            })
                        
                        # Create comparison plot
                        fig = go.Figure()
                        colors = ['#3498db', '#e74c3c']
                        
                        for i, scenario in enumerate(scenarios):
                            # Historical data
                            fig.add_trace(
                                go.Scatter(
                                    x=[p['date'] for p in scenario['historical_data']],
                                    y=[p['value'] for p in scenario['historical_data']],
                                    mode='lines',
                                    name=f"{scenario['name']} (Historical)",
                                    line=dict(color=colors[i], width=2)
                                )
                            )
                            
                            # Prediction
                            forecast = scenario['prediction']['forecast']
                            fig.add_trace(
                                go.Scatter(
                                    x=[p['date'] for p in forecast],
                                    y=[p['value'] for p in forecast],
                                    mode='lines',
                                    name=f"{scenario['name']} (Predicted)",
                                    line=dict(color=colors[i], width=2, dash='dash')
                                )
                            )
                            
                            # Confidence interval
                            fig.add_trace(
                                go.Scatter(
                                    x=[p['date'] for p in forecast] + [p['date'] for p in forecast][::-1],
                                    y=[p['upper_bound'] for p in forecast] + [p['lower_bound'] for p in forecast][::-1],
                                    fill='toself',
                                    fillcolor=f'rgba{tuple(list(int(colors[i].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
                                    line=dict(color='rgba(255,255,255,0)'),
                                    showlegend=False,
                                    name=f"{scenario['name']} Confidence"
                                )
                            )
                        
                        fig.update_layout(
                            title="Supply Predictions Comparison",
                            xaxis_title="Date",
                            yaxis_title="Supply",
                            hovermode='x unified',
                            showlegend=True
                        )
                        
                        # Display plot
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display metrics
                        st.subheader("Comparison Metrics")
                        metrics_df = pd.DataFrame([
                            {
                                "Scenario": scenario['name'],
                                "RMSE": scenario['prediction']['metrics']['rmse'],
                                "MAE": scenario['prediction']['metrics']['mae']
                            }
                            for scenario in scenarios
                        ])
                        st.dataframe(metrics_df)
                        
                        # Export button
                        if st.button("Export PDF Report"):
                            pdf_bytes = generate_pdf_report(scenarios, fig)
                            st.download_button(
                                label="Download PDF",
                                data=pdf_bytes,
                                file_name="predictions-comparison.pdf",
                                mime="application/pdf"
                            )
                    
                    except Exception as e:
                        st.error(f"Error generating predictions: {str(e)}")

if __name__ == "__main__":
    main() 
