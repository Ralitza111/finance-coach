"""
Market Data API Integration

Handles all interactions with financial market data APIs (Alpha Vantage & yFinance)
for fetching stock quotes, historical data, and market information.
"""

import requests
import time
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketDataAPI:
    """Wrapper for market data API calls using Alpha Vantage and yFinance"""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        Initialize Market Data API client
        
        Args:
            alpha_vantage_key: Alpha Vantage API key (optional, yFinance will be used as fallback)
        """
        self.alpha_vantage_key = alpha_vantage_key
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        
        # Rate limiting for both APIs
        self.last_request_time = 0
        self.min_request_interval = 3  # 3 seconds between yFinance requests to avoid 429
        
        # Cache for recent requests to reduce API calls
        self.cache = {}
        self.cache_duration = 300  # Cache data for 5 minutes (300 seconds)
        
        logger.info("MarketDataAPI initialized")
    
    def _rate_limit(self):
        """Implement rate limiting to avoid 429 errors"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if available and not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any):
        """Save data to cache with timestamp"""
        self.cache[cache_key] = (data, time.time())
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time stock quote for a symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Dictionary with stock quote data or None if failed
        """
        logger.info(f"Fetching stock quote for {symbol}")
        
        # Check cache first
        cache_key = f"quote_{symbol}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"✅ Returning cached quote for {symbol}")
            return cached_data
        
        # Rate limit to avoid 429 errors
        self._rate_limit()
        
        try:
            # Use yFinance as primary source
            ticker = yf.Ticker(symbol)
            
            current_price = None
            previous_close = None
            name = symbol
            market_cap = 'N/A'
            pe_ratio = 'N/A'
            
            # Method 1: Try historical data first (most reliable, less rate-limited)
            try:
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    if len(hist) > 1:
                        previous_close = float(hist['Close'].iloc[-2])
                    else:
                        previous_close = float(hist['Open'].iloc[-1])
                    logger.debug(f"Got price from history for {symbol}: ${current_price}")
            except Exception as hist_error:
                logger.debug(f"History method failed for {symbol}: {hist_error}")
            
            # Method 2: Try fast_info if history failed
            if current_price is None or current_price == 0:
                try:
                    fast_info = ticker.fast_info
                    current_price = float(fast_info.get('last_price', 0))
                    previous_close = float(fast_info.get('previous_close', current_price))
                    if current_price > 0:
                        logger.debug(f"Got price from fast_info for {symbol}: ${current_price}")
                except Exception as fast_error:
                    logger.debug(f"Fast info method failed for {symbol}: {fast_error}")
            
            # If we still don't have a valid price, return error
            if current_price is None or current_price == 0:
                logger.warning(f"Could not fetch valid price for {symbol}")
                return {
                    'symbol': symbol.upper(),
                    'name': symbol,
                    'price': 'N/A',
                    'change': 'N/A',
                    'change_percent': 'N/A',
                    'error': 'Real-time data temporarily unavailable. The data provider may be rate-limiting requests. Please try again in a moment.',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Calculate change
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close) * 100 if previous_close and previous_close != 0 else 0
            
            # Try to get additional info (with error handling for 429)
            try:
                info = ticker.info
                name = info.get('longName', symbol)
                market_cap = info.get('marketCap', 'N/A')
                pe_ratio = info.get('trailingPE', 'N/A')
            except Exception as info_error:
                logger.debug(f"Could not fetch detailed info for {symbol}: {info_error}")
            
            quote_data = {
                'symbol': symbol.upper(),
                'name': name,
                'price': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'previous_close': round(float(previous_close), 2) if previous_close else 'N/A',
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Cache the result
            self._save_to_cache(cache_key, quote_data)
            
            logger.info(f"✅ Successfully fetched quote for {symbol}: ${quote_data['price']}")
            return quote_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching quote for {symbol}: {e}")
            # Return a minimal fallback response
            return {
                'symbol': symbol.upper(),
                'name': symbol,
                'price': 'N/A',
                'change': 'N/A',
                'change_percent': 'N/A',
                'error': 'Real-time data temporarily unavailable. The data provider may be experiencing high traffic. Please try again shortly.',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[Dict[str, Any]]:
        """
        Get historical price data for a symbol
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dictionary with historical data or None if failed
        """
        logger.info(f"Fetching historical data for {symbol} ({period})")
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            # Calculate statistics
            current_price = hist['Close'].iloc[-1]
            period_high = hist['High'].max()
            period_low = hist['Low'].min()
            period_start = hist['Close'].iloc[0]
            period_change = current_price - period_start
            period_change_percent = (period_change / period_start) * 100
            
            avg_volume = hist['Volume'].mean()
            
            historical_data = {
                'symbol': symbol.upper(),
                'period': period,
                'current_price': round(current_price, 2),
                'period_high': round(period_high, 2),
                'period_low': round(period_low, 2),
                'period_start_price': round(period_start, 2),
                'period_change': round(period_change, 2),
                'period_change_percent': round(period_change_percent, 2),
                'average_volume': int(avg_volume),
                'data_points': len(hist),
                'start_date': hist.index[0].strftime('%Y-%m-%d'),
                'end_date': hist.index[-1].strftime('%Y-%m-%d'),
                'raw_data': hist.to_dict('index')  # Full historical data
            }
            
            logger.info(f"✅ Successfully fetched {len(hist)} data points for {symbol}")
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company information
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with company information or None if failed
        """
        logger.info(f"Fetching company info for {symbol}")
        
        # Check cache first
        cache_key = f"company_{symbol}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"✅ Returning cached company info for {symbol}")
            return cached_data
        
        # Rate limit to avoid 429 errors
        self._rate_limit()
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get basic info with error handling
            try:
                info = ticker.info
                company_data = {
                    'symbol': symbol.upper(),
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'description': info.get('longBusinessSummary', 'N/A')[:500] + '...' if info.get('longBusinessSummary') else 'N/A',
                    'website': info.get('website', 'N/A'),
                    'market_cap': info.get('marketCap', 'N/A'),
                    'employees': info.get('fullTimeEmployees', 'N/A'),
                    'headquarters': f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(', '),
                    'pe_ratio': info.get('trailingPE', 'N/A'),
                    'forward_pe': info.get('forwardPE', 'N/A'),
                    'dividend_yield': info.get('dividendYield', 'N/A'),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                    '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                }
            except Exception as info_error:
                logger.warning(f"Could not fetch detailed company info for {symbol}: {info_error}")
                # Return minimal info
                company_data = {
                    'symbol': symbol.upper(),
                    'name': symbol,
                    'sector': 'N/A',
                    'industry': 'N/A',
                    'description': 'Information temporarily unavailable due to rate limiting',
                    'error': 'Data temporarily unavailable'
                }
            
            # Cache the result
            self._save_to_cache(cache_key, company_data)
            
            logger.info(f"✅ Successfully fetched company info for {symbol}")
            return company_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching company info for {symbol}: {e}")
            return {
                'symbol': symbol.upper(),
                'name': symbol,
                'error': 'Data temporarily unavailable',
                'description': 'Company information could not be retrieved at this time due to rate limiting. Please try again in a moment.'
            }
    
    def get_market_indices(self) -> Dict[str, Any]:
        """
        Get current data for major market indices
        
        Returns:
            Dictionary with major index data
        """
        logger.info("Fetching major market indices")
        
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000'
        }
        
        results = {}
        
        for symbol, name in indices.items():
            quote = self.get_stock_quote(symbol)
            if quote:
                results[name] = {
                    'symbol': symbol,
                    'price': quote['price'],
                    'change': quote['change'],
                    'change_percent': quote['change_percent']
                }
        
        logger.info(f"✅ Fetched data for {len(results)} indices")
        return results
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """
        Search for stock symbols matching a query
        
        Args:
            query: Company name or ticker to search
            
        Returns:
            List of matching symbols with basic info
        """
        logger.info(f"Searching symbols for query: {query}")
        
        # This is a simplified search - in production, use a proper search API
        # For now, try to fetch the ticker directly
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            
            if 'symbol' in info:
                return [{
                    'symbol': info.get('symbol', query.upper()),
                    'name': info.get('longName', 'N/A'),
                    'type': info.get('quoteType', 'EQUITY'),
                    'exchange': info.get('exchange', 'N/A')
                }]
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Error searching for {query}: {e}")
            return []
    
    def get_trending_stocks(self) -> List[str]:
        """
        Get list of trending/popular stocks
        
        Returns:
            List of trending stock symbols
        """
        # Predefined list of popular stocks to analyze
        # In production, could use Yahoo Finance trending or similar API
        trending = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'NVDA', 'META', 'BRK-B', 'JPM', 'V'
        ]
        
        logger.info(f"Returning {len(trending)} trending stocks")
        return trending
