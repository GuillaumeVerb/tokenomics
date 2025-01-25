from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from pycoingecko import CoinGeckoAPI
import os
from dotenv import load_dotenv

mongo = PyMongo()
cg = CoinGeckoAPI()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config["MONGO_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/tokenomics")
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Register blueprints
    from app.routes.market_data import market_data_bp
    app.register_blueprint(market_data_bp, url_prefix='/api/market-data')
    
    return app 