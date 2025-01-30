"""Type stubs for pycoingecko."""
from typing import Any, Dict, List, Optional, Union

class CoinGeckoAPI:
    def __init__(self, api_key: Optional[str] = None) -> None: ...
    
    def get_price(
        self,
        ids: Union[str, List[str]],
        vs_currencies: Union[str, List[str]],
        include_market_cap: bool = False,
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
        include_last_updated_at: bool = False,
        precision: Optional[str] = None,
    ) -> Dict[str, Dict[str, float]]: ...
    
    def get_coin_history_by_id(
        self,
        id: str,
        date: str,
        localization: bool = True,
    ) -> Dict[str, Any]: ...
    
    def get_coin_market_chart_by_id(
        self,
        id: str,
        vs_currency: str,
        days: Union[int, str],
        interval: Optional[str] = None,
    ) -> Dict[str, List[List[float]]]: ...
    
    def get_coin_market_chart_range_by_id(
        self,
        id: str,
        vs_currency: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> Dict[str, List[List[float]]]: ...
    
    def get_coins_markets(
        self,
        vs_currency: str,
        ids: Optional[Union[str, List[str]]] = None,
        category: Optional[str] = None,
        order: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        sparkline: bool = False,
        price_change_percentage: Optional[str] = None,
    ) -> List[Dict[str, Any]]: ... 