import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from typing import Dict
import os

# Configuration
API_URL = os.getenv('API_URL', 'http://localhost:8000')
API_TOKEN = os.getenv('API_TOKEN', '')

def simulate_inflation(total_supply: int, inflation_rate: float, years: int) -> Dict:
    """Call the API to simulate constant inflation."""
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    response = requests.post(
        f'{API_URL}/simulate/constant_inflation',
        headers=headers,
        json={
            'initial_supply': total_supply,
            'inflation_rate': inflation_rate,
            'duration_in_years': years
        }
    )
    return response.json()

# Page config
st.set_page_config(page_title='Tokenomics Simulator', layout='wide')
st.title('Simulation d\'Inflation Constante')

# Input form
with st.form('simulation_form'):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_supply = st.number_input(
            'Supply Initiale',
            min_value=1,
            value=1000000,
            step=1000
        )
    
    with col2:
        inflation_rate = st.number_input(
            'Taux d\'Inflation (%)',
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1
        )
    
    with col3:
        years = st.number_input(
            'Durée (années)',
            min_value=1,
            max_value=50,
            value=5
        )
    
    submitted = st.form_submit_button('Simuler')

# Handle simulation
if submitted:
    try:
        # Get simulation results
        results = simulate_inflation(total_supply, inflation_rate, years)
        
        # Convert to DataFrame
        df = pd.DataFrame(results['simulation_data'])
        
        # Display results
        st.subheader('Résultats de la Simulation')
        
        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                'Supply Finale',
                f'{df.iloc[-1].supply:,.0f}',
                f'+{results["total_supply_increase"]:,.0f}'
            )
        with col2:
            st.metric(
                'Augmentation Totale',
                f'{results["total_supply_increase_percentage"]:.1f}%'
            )
        
        # Graph
        fig = px.line(
            df,
            x='year',
            y='supply',
            title='Évolution de la Supply',
            labels={'year': 'Année', 'supply': 'Supply Totale'}
        )
        fig.update_layout(
            showlegend=False,
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader('Données Détaillées')
        st.dataframe(df.style.format({'supply': '{:,.0f}'}))
        
        # CSV Export
        csv = df.to_csv(index=False)
        st.download_button(
            'Télécharger CSV',
            csv,
            'simulation_results.csv',
            'text/csv'
        )
        
    except Exception as e:
        st.error(f'Erreur lors de la simulation: {str(e)}') 