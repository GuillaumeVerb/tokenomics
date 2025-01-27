"""
Airflow DAG to orchestrate market data collection and tokenomics simulation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.utils.email import send_email

import pandas as pd
import requests
from services.market_data import fetch_coingecko_data

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your-email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def clean_market_data(**context) -> None:
    """
    Clean market data in MongoDB by:
    1. Removing duplicates
    2. Handling missing values
    3. Converting data types
    4. Adding metadata
    """
    mongo = MongoHook(mongo_conn_id='mongo_default')
    db = mongo.get_database()
    collection = db.market_data

    # Get the latest timestamp for each token
    pipeline = [
        {
            '$sort': {'timestamp': -1}
        },
        {
            '$group': {
                '_id': '$token_id',
                'latest_doc': {'$first': '$$ROOT'}
            }
        }
    ]
    latest_docs = list(collection.aggregate(pipeline))

    # Process and update each document
    for doc in latest_docs:
        token_id = doc['_id']
        latest = doc['latest_doc']

        # Clean and validate price data
        if latest.get('price_usd') is not None:
            # Remove any documents with invalid prices
            collection.delete_many({
                'token_id': token_id,
                'price_usd': {'$exists': False}
            })

            # Update metadata
            collection.update_many(
                {'token_id': token_id},
                {
                    '$set': {
                        'last_updated': datetime.utcnow(),
                        'data_quality': 'cleaned'
                    }
                }
            )

    context['task_instance'].xcom_push(
        key='cleaned_tokens',
        value=len(latest_docs)
    )

def check_simulation_needed(**context) -> bool:
    """
    Check if we need to run a new simulation based on price changes.
    Returns True if simulation is needed.
    """
    mongo = MongoHook(mongo_conn_id='mongo_default')
    db = mongo.get_database()
    collection = db.market_data

    # Get price changes in the last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    pipeline = [
        {
            '$match': {
                'timestamp': {'$gte': one_hour_ago}
            }
        },
        {
            '$group': {
                '_id': '$token_id',
                'price_change': {
                    '$max': '$price_change_percentage.24h'
                }
            }
        }
    ]
    price_changes = list(collection.aggregate(pipeline))

    # If any token has changed more than 5%, trigger simulation
    needs_simulation = any(
        abs(doc.get('price_change', 0) or 0) > 5.0
        for doc in price_changes
    )

    context['task_instance'].xcom_push(
        key='simulation_needed',
        value=needs_simulation
    )
    return needs_simulation

def prepare_simulation_request(**context) -> Dict[str, Any]:
    """
    Prepare the request body for the simulation API.
    """
    mongo = MongoHook(mongo_conn_id='mongo_default')
    db = mongo.get_database()
    collection = db.market_data

    # Get latest prices
    pipeline = [
        {
            '$sort': {'timestamp': -1}
        },
        {
            '$group': {
                '_id': '$token_id',
                'latest_price': {'$first': '$price_usd'}
            }
        }
    ]
    latest_prices = list(collection.aggregate(pipeline))

    # Prepare simulation parameters
    request_body = {
        'initial_supply': 1000000,
        'time_step': 'hourly',
        'duration': 24,
        'inflation_config': {
            'type': 'dynamic',
            'base_rate': 5,
            'market_factor': 0.5,
            'current_prices': {
                doc['_id']: doc['latest_price']
                for doc in latest_prices
            }
        }
    }

    return request_body

def send_success_notification(context):
    """
    Send success notification to Slack.
    """
    cleaned_tokens = context['task_instance'].xcom_pull(
        key='cleaned_tokens',
        task_ids='clean_market_data'
    )
    simulation_needed = context['task_instance'].xcom_pull(
        key='simulation_needed',
        task_ids='check_simulation'
    )

    message = (
        f"✅ Market Data Pipeline Completed Successfully\n"
        f"• Cleaned data for {cleaned_tokens} tokens\n"
        f"• Simulation {'was' if simulation_needed else 'was not'} needed\n"
        f"• Execution time: {context['execution_date']}"
    )

    return message

def send_error_notification(context):
    """
    Send error notification via email.
    """
    task_id = context['task_instance'].task_id
    error = context.get('exception')
    
    subject = f"❌ Market Data Pipeline Failed - {task_id}"
    html_content = f"""
    <h3>Pipeline Failure</h3>
    <p><strong>Task:</strong> {task_id}</p>
    <p><strong>Error:</strong> {str(error)}</p>
    <p><strong>Execution Time:</strong> {context['execution_date']}</p>
    """

    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=html_content
    )

# Create the DAG
with DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='Fetch market data and update tokenomics simulations',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['market_data', 'tokenomics'],
    on_failure_callback=send_error_notification
) as dag:

    # Task 1: Fetch market data
    fetch_data = PythonOperator(
        task_id='fetch_market_data',
        python_callable=fetch_coingecko_data,
        retries=3,
        retry_delay=timedelta(minutes=2)
    )

    # Task 2: Clean market data
    clean_data = PythonOperator(
        task_id='clean_market_data',
        python_callable=clean_market_data
    )

    # Task 3: Check if simulation is needed
    check_simulation = PythonOperator(
        task_id='check_simulation',
        python_callable=check_simulation_needed
    )

    # Task 4: Run simulation if needed
    run_simulation = SimpleHttpOperator(
        task_id='run_simulation',
        http_conn_id='tokenomics_api',
        endpoint='/simulate/scenario',
        method='POST',
        data=prepare_simulation_request,
        response_check=lambda response: response.status_code == 200,
        trigger_rule='none_failed'
    )

    # Task 5: Send success notification
    notify_success = SlackWebhookOperator(
        task_id='notify_success',
        http_conn_id='slack_webhook',
        message=send_success_notification,
        trigger_rule='none_failed'
    )

    # Define task dependencies
    fetch_data >> clean_data >> check_simulation >> run_simulation >> notify_success 