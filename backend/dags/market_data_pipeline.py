"""
Market data pipeline DAG for fetching and processing cryptocurrency market data.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Sequence

import pandas as pd  # type: ignore
from airflow import DAG  # type: ignore
from airflow.operators.python import PythonOperator  # type: ignore
from airflow.providers.http.operators.http import SimpleHttpOperator  # type: ignore

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_market_data(**context: Any) -> Sequence[Dict[str, Any]]:  # type: ignore
    """Process market data fetched from CoinGecko."""
    # Get the response from the previous task
    ti = context['task_instance']
    response = ti.xcom_pull(task_ids='fetch_market_data')
    
    # Convert to DataFrame
    df = pd.DataFrame(response)  # type: ignore
    
    # Process data as needed
    # Add your processing logic here
    processed_df = df[['id', 'symbol', 'name', 'current_price', 'market_cap', 'total_volume']]  # type: ignore
    processed_df['timestamp'] = datetime.utcnow()  # type: ignore
    
    return processed_df.to_dict(orient='records')  # type: ignore

# Create the DAG
dag = DAG(  # type: ignore
    'market_data_pipeline',
    default_args=default_args,
    description='A DAG to fetch and process market data',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Define tasks
fetch_market_data = SimpleHttpOperator(  # type: ignore
    task_id='fetch_market_data',
    http_conn_id='coingecko_api',
    endpoint='/api/v3/coins/markets',
    method='GET',
    data={
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': False
    },
    headers={},
    response_filter=lambda response: response.json(),
    dag=dag,
)

process_data = PythonOperator(  # type: ignore
    task_id='process_data',
    python_callable=process_market_data,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
fetch_market_data.set_downstream(process_data)  # type: ignore 