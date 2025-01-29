from typing import Dict, List, Optional

from app.core.config import settings
from app.services.market_data_service import get_token_market_data
from fastapi import APIRouter, HTTPException
from pycoingecko import CoinGeckoAPI
from pymongo import MongoClient

# Initialize CoinGecko client
cg = CoinGeckoAPI()

# Initialize MongoDB client
mongo_client = MongoClient(settings.MONGODB_URI)
db = mongo_client[settings.MONGODB_NAME]

router = APIRouter(prefix="/market-data", tags=["Market Data"])

@router.get(
    "/token/{token_id}",
    response_model=Dict,
    summary="Get token market data",
    description="Retrieve market data for a specific token by its ID"
)
async def get_token_data(token_id: str) -> Dict:
    """
    Get market data for a specific token.
    
    Args:
        token_id: The CoinGecko ID of the token
        
    Returns:
        Dict containing market data
        
    Raises:
        HTTPException: If token is not found or there's an error
    """
    try:
        market_data = get_token_market_data(token_id)
        return market_data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching token data: {str(e)}"
        )

@router.get(
    "/trending",
    response_model=List[Dict],
    summary="Get trending tokens",
    description="Get a list of trending tokens from CoinGecko"
)
async def get_trending_tokens() -> List[Dict]:
    """
    Get trending tokens from CoinGecko.
    
    Returns:
        List of trending tokens
        
    Raises:
        HTTPException: If there's an error fetching trending data
    """
    try:
        trending = cg.get_search_trending()
        # Extract coins from the response
        trending_coins = trending.get('coins', [])
        return trending_coins
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching trending tokens: {str(e)}"
        )

@router.get(
    "/search/{query}",
    response_model=List[Dict],
    summary="Search tokens",
    description="Search for tokens by name or symbol"
)
async def search_tokens(
    query: str,
    limit: Optional[int] = 10
) -> List[Dict]:
    """
    Search for tokens using CoinGecko API.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of matching tokens
        
    Raises:
        HTTPException: If there's an error during search
    """
    try:
        results = cg.search(query)
        coins = results.get('coins', [])
        
        # Sort by market cap rank and limit results
        sorted_coins = sorted(
            coins,
            key=lambda x: x.get('market_cap_rank') or float('inf')
        )
        return sorted_coins[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching tokens: {str(e)}"
        ) 