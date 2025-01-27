"""
Service for fetching and storing cryptocurrency market data from CoinGecko.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any

import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from requests.exceptions import RequestException, Timeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
TIMEOUT_SECONDS = 10
RATE_LIMIT_PAUSE = 60  # Pause duration when rate limit is hit
MAX_RETRIES = 3

# Token IDs to track
TOKENS = [
    "bitcoin",
    "ethereum",
    "binancecoin",
    "cardano",
    "solana",
    "polkadot",
    "avalanche-2",
]

def get_mongodb_collection() -> Collection:
    """
    Get MongoDB collection for market data.
    
    Returns:
        Collection: MongoDB collection object
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client.tokenomics
    return db.market_data

def fetch_coingecko_data(tokens: List[str] = TOKENS) -> None:
    """
    Fetch current market data for specified tokens from CoinGecko and store in MongoDB.
    
    Args:
        tokens: List of token IDs to fetch data for. Defaults to predefined TOKENS list.
    
    Raises:
        RequestException: If there's an error fetching data from CoinGecko
        Timeout: If the request times out
    """
    collection = get_mongodb_collection()
    
    # Parameters for the CoinGecko API request
    params = {
        'vs_currency': 'usd',
        'ids': ','.join(tokens),
        'order': 'market_cap_desc',
        'per_page': len(tokens),
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '24h,7d,30d'
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            # Make request to CoinGecko API
            response = requests.get(
                f"{COINGECKO_API_URL}/coins/markets",
                params=params,
                timeout=TIMEOUT_SECONDS
            )
            
            # Check for rate limit
            if response.status_code == 429:
                logger.warning("Rate limit hit, pausing for %d seconds", RATE_LIMIT_PAUSE)
                time.sleep(RATE_LIMIT_PAUSE)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            # Prepare documents for MongoDB
            timestamp = datetime.utcnow()
            documents = []
            
            for token in data:
                document = {
                    'token_id': token['id'],
                    'symbol': token['symbol'].upper(),
                    'name': token['name'],
                    'timestamp': timestamp,
                    'price_usd': token.get('current_price'),
                    'market_cap': token.get('market_cap'),
                    'total_volume': token.get('total_volume'),
                    'circulating_supply': token.get('circulating_supply'),
                    'total_supply': token.get('total_supply'),
                    'max_supply': token.get('max_supply'),
                    'price_change_percentage': {
                        '24h': token.get('price_change_percentage_24h'),
                        '7d': token.get('price_change_percentage_7d'),
                        '30d': token.get('price_change_percentage_30d')
                    }
                }
                documents.append(document)
            
            # Store in MongoDB
            if documents:
                collection.insert_many(documents)
                logger.info(
                    "Successfully stored market data for %d tokens",
                    len(documents)
                )
            
            break  # Success, exit retry loop
            
        except Timeout:
            logger.error(
                "Timeout fetching data from CoinGecko (attempt %d/%d)",
                attempt + 1,
                MAX_RETRIES
            )
            if attempt == MAX_RETRIES - 1:
                raise
                
        except RequestException as e:
            logger.error(
                "Error fetching data from CoinGecko: %s (attempt %d/%d)",
                str(e),
                attempt + 1,
                MAX_RETRIES
            )
            if attempt == MAX_RETRIES - 1:
                raise
        except KeyError as e:
            logger.error(
                "Error processing token data: %s (attempt %d/%d)",
                str(e),
                attempt + 1,
                MAX_RETRIES
            )
            if attempt == MAX_RETRIES - 1:
                raise

def create_market_data_indexes() -> None:
    """
    Create indexes on the market_data collection for better query performance.
    """
    collection = get_mongodb_collection()
    
    # Create indexes
    collection.create_index([("token_id", 1), ("timestamp", -1)])
    collection.create_index("timestamp")
    
    logger.info("Created indexes on market_data collection")

if __name__ == "__main__":
    # Example usage
    try:
        # Ensure indexes exist
        create_market_data_indexes()
        
        # Fetch data
        fetch_coingecko_data()
        
    except Exception as e:
        logger.error("Error in market data service: %s", str(e)) 