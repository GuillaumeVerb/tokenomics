#!/usr/bin/env python3
"""
Script to fetch market data from CoinGecko and store in MongoDB.
Can be run manually or scheduled via cron.

Example crontab entry to run every 5 minutes:
*/5 * * * * /path/to/venv/bin/python /path/to/fetch_market_data.py

Make sure to make the script executable:
chmod +x fetch_market_data.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from services.market_data import fetch_coingecko_data, create_market_data_indexes

# Configure logging to file
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "market_data.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to fetch and store market data.
    """
    try:
        # Ensure indexes exist
        create_market_data_indexes()
        
        # Fetch and store market data
        fetch_coingecko_data()
        
    except Exception as e:
        logger.error("Error fetching market data: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 