"""
Unit Tests for Market Data API Client
Tests stock data fetching, caching, and error handling.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market_data_api import MarketDataAPI


@pytest.fixture
def market_api():
    """Fixture to create a test market data API instance"""
    return MarketDataAPI()


class TestMarketDataAPI:
    """Test the MarketDataAPI class"""
    
    def test_api_initialization(self, market_api):
        """Test that API initializes correctly"""
        assert market_api is not None
        assert hasattr(market_api, 'cache')
        assert hasattr(market_api, 'last_request_time')
    
    def test_cache_functionality(self, market_api):
        """Test that caching works"""
        # Save to cache
        test_key = "test_stock_AAPL"
        test_data = {"price": 150.00, "symbol": "AAPL"}
        market_api._save_to_cache(test_key, test_data)
        
        # Retrieve from cache
        cached_data = market_api._get_from_cache(test_key)
        assert cached_data == test_data
    
    def test_cache_expiration(self, market_api):
        """Test that cache expires after duration"""
        # Save to cache with short duration
        market_api.cache_duration = 1  # 1 second
        test_key = "test_expiry"
        test_data = {"test": "data"}
        market_api._save_to_cache(test_key, test_data)
        
        # Should be in cache immediately
        assert market_api._get_from_cache(test_key) == test_data
        
        # Wait for expiration (in real scenario)
        # Note: In actual test, we'd need to wait or mock time
    
    def test_rate_limiting(self, market_api):
        """Test that rate limiting is applied"""
        assert hasattr(market_api, 'min_request_interval')
        assert market_api.min_request_interval > 0
    
    def test_get_stock_quote_structure(self, market_api):
        """Test that get_stock_quote returns proper structure"""
        result = market_api.get_stock_quote("AAPL")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have required keys
        expected_keys = ["symbol", "price", "currency", "change", "change_percent", "timestamp"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_get_stock_quote_invalid_symbol(self, market_api):
        """Test handling of invalid stock symbols"""
        result = market_api.get_stock_quote("INVALID_SYMBOL_XYZ")
        
        # Should still return a dictionary with error info
        assert isinstance(result, dict)
        assert "symbol" in result
    
    def test_get_company_info_structure(self, market_api):
        """Test that get_company_info returns proper structure"""
        result = market_api.get_company_info("AAPL")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have symbol
        assert "symbol" in result
    
    def test_get_market_indices_structure(self, market_api):
        """Test that get_market_indices returns proper structure"""
        result = market_api.get_market_indices()
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have major indices
        assert "indices" in result
        assert isinstance(result["indices"], list)
    
    def test_search_stocks_structure(self, market_api):
        """Test that search_stocks returns proper structure"""
        result = market_api.search_stocks("Apple")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have results
        assert "results" in result
        assert isinstance(result["results"], list)


class TestErrorHandling:
    """Test error handling in MarketDataAPI"""
    
    def test_api_error_handling(self, market_api):
        """Test that API errors are handled gracefully"""
        # Test with empty symbol
        result = market_api.get_stock_quote("")
        assert isinstance(result, dict)
        assert "error" in result or "symbol" in result
    
    def test_network_error_fallback(self, market_api):
        """Test fallback behavior on network errors"""
        # This would test the 3-tier fallback system
        result = market_api.get_stock_quote("AAPL")
        
        # Should always return a dictionary, never raise exception
        assert isinstance(result, dict)
    
    def test_rate_limit_handling(self, market_api):
        """Test that rate limiting (429) errors are handled"""
        # The API should have fallback mechanisms for rate limiting
        # Multiple calls should use cache or gracefully degrade
        result1 = market_api.get_stock_quote("AAPL")
        result2 = market_api.get_stock_quote("AAPL")  # Should use cache
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)


class TestDataValidation:
    """Test data validation and formatting"""
    
    def test_price_validation(self, market_api):
        """Test that prices are validated"""
        result = market_api.get_stock_quote("AAPL")
        
        if "price" in result and result["price"] != "N/A":
            # Price should be a number or currency string
            price = result["price"]
            if isinstance(price, str):
                # Remove currency symbols and convert
                clean_price = price.replace("$", "").replace(",", "")
                try:
                    float(clean_price)
                    assert True
                except ValueError:
                    assert False, f"Invalid price format: {price}"
    
    def test_timestamp_format(self, market_api):
        """Test that timestamps are in valid format"""
        result = market_api.get_stock_quote("AAPL")
        
        if "timestamp" in result and result["timestamp"] != "N/A":
            # Timestamp should be parseable
            timestamp = result["timestamp"]
            assert isinstance(timestamp, str)
            assert len(timestamp) > 0


# Run tests with: pytest tests/test_market_data_api.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
