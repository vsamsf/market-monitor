"""Market data fetcher for Indian stock indices."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
from utils.logger import get_logger
from utils.helpers import get_ist_now, calculate_change_percent

logger = get_logger(__name__)


class MarketDataFetcher:
    """Fetch market data from Yahoo Finance."""
    
    def __init__(self):
        """Initialize market data fetcher."""
        self.cache = {}
        self.cache_expiry = timedelta(minutes=5)
    
    def fetch_index_data(self, symbol: str, name: str) -> Optional[Dict]:
        """
        Fetch data for a single index, prioritizing historical data.
        Historical data API has better rate limits than real-time info API.
        
        Args:
            symbol: Index symbol (e.g., ^NSEI for NIFTY 50)
            name: Index display name
        
        Returns:
            Dictionary with index data or None on error
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{name}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if get_ist_now() - cached_time < self.cache_expiry:
                    logger.debug(f"Returning cached data for {name}")
                    return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # PRIORITIZE historical data (better rate limits, works after market close)
            logger.info(f"Fetching historical data for {symbol}")
            hist = ticker.history(period="5d")
            
            if hist.empty:
                logger.error(f"No historical data available for {symbol}")
                return None
            
            # Get the latest close as current price (today's close if market is closed)
            current_price = hist['Close'].iloc[-1]
            
            # Get previous close (from 1 trading day before)
            if len(hist) >= 2:
                previous_close = hist['Close'].iloc[-2]
            else:
                previous_close = current_price
                logger.warning(f"Only 1 day of data for {symbol}, using same price")
            
            # Calculate change
            change = current_price - previous_close
            change_percent = calculate_change_percent(current_price, previous_close)
            
            # Get the timestamp of the data
            data_timestamp = hist.index[-1].to_pydatetime()
            
            data = {
                'symbol': symbol,
                'name': name,
                'current_price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'timestamp': data_timestamp,
                'is_real_data': True  # Flag to indicate this is real data
            }
            
            # Update cache
            self.cache[cache_key] = (data, get_ist_now())
            
            logger.info(f"✓ Fetched REAL data for {name}: {current_price} ({change_percent:+.2f}%)")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_multiple_indices(self, index_configs: List[Dict]) -> List[Dict]:
        """
        Fetch data for multiple indices.
        
        Args:
            index_configs: List of index configurations
        
        Returns:
            List of index data dictionaries
        """
        indices_data = []
        
        for config in index_configs:
            data = self.fetch_index_data(config['symbol'], config['name'])
            if data:
                indices_data.append(data)
        
        # Only use demo data if we got ZERO real data
        if len(indices_data) == 0:
            logger.warning("⚠️ All real data fetches failed, using demo data as fallback")
            try:
                from market_monitor.demo_data import get_demo_indices
                demo_data = get_demo_indices()
                # Mark as demo data
                for item in demo_data:
                    item['is_demo_data'] = True
                return demo_data
            except Exception as e:
                logger.error(f"Failed to load demo data: {e}")
                return []
        
        return indices_data
    
    def fetch_top_gainers_losers(self, index_symbol: str = "^NSEI", limit: int = 5) -> Dict[str, List[Dict]]:
        """
        Fetch top gainers and losers from an index.
        
        Args:
            index_symbol: Index symbol
            limit: Number of top gainers/losers to return
        
        Returns:
            Dictionary with 'gainers' and 'losers' lists
        """
        try:
            # For now, we'll use a simplified approach
            # In production, you might want to use NSE API or scrape data
            
            # Get NIFTY 50 constituents (simplified - you'd need actual constituent list)
            # This is a placeholder implementation
            logger.warning("Top gainers/losers feature requires NSE API integration")
            
            return {
                'gainers': [],
                'losers': []
            }
            
        except Exception as e:
            logger.error(f"Error fetching top gainers/losers: {e}")
            return {'gainers': [], 'losers': []}
    
    def get_sector_performance(self) -> List[Dict]:
        """
        Get sector performance data.
        
        Returns:
            List of sector performance data
        """
        try:
            # Sector indices mapping
            sectors = {
                'NIFTY BANK': '^NSEBANK',
                'NIFTY IT': '^CNXIT',
                'NIFTY AUTO': '^CNXAUTO',
                'NIFTY PHARMA': '^CNXPHARMA',
                'NIFTY FMCG': '^CNXFMCG'
            }
            
            sector_data = []
            for name, symbol in sectors.items():
                data = self.fetch_index_data(symbol, name)
                if data:
                    sector_data.append({
                        'sector': name,
                        'change_percent': data['change_percent']
                    })
            
            # Sort by performance
            sector_data.sort(key=lambda x: x['change_percent'], reverse=True)
            
            return sector_data
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return []
    
    def clear_cache(self):
        """Clear the data cache."""
        self.cache = {}
        logger.info("Market data cache cleared")
