from app import cg, mongo
from datetime import datetime

def get_token_market_data(token_id):
    # Récupérer les données via CoinGecko
    market_data = cg.get_coin_by_id(
        id=token_id,
        localization=False,
        tickers=False,
        market_data=True,
        community_data=False,
        developer_data=False,
        sparkline=False
    )
    
    # Préparer les données pour stockage
    processed_data = {
        "token_id": token_id,
        "price_usd": market_data["market_data"]["current_price"]["usd"],
        "market_cap": market_data["market_data"]["market_cap"]["usd"],
        "volume_24h": market_data["market_data"]["total_volume"]["usd"],
        "timestamp": datetime.utcnow()
    }
    
    # Sauvegarder dans MongoDB
    mongo.db.market_data.insert_one(processed_data)
    
    return processed_data 