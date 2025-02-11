from pycoingecko import CoinGeckoAPI
from pymongo import MongoClient

from .config import settings

# Initialize CoinGecko client
cg = CoinGeckoAPI(api_key=settings.COINGECKO_API_KEY)

# Initialize MongoDB client
mongo_client = MongoClient(settings.MONGODB_URL)
mongo_db = mongo_client[settings.MONGODB_DB_NAME]
