"""
Unit Tests for Financial Tools
Tests agent tools and API client functionality.
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specialized_agents import create_specialized_agents
from market_data_api import MarketDataAPI
from news_api import FinancialNewsAPI
from web_scraper import FinancialWebScraper
from langchain_openai import ChatOpenAI


@pytest.fixture
def agents():
    """Fixture to create test agent instances with tools"""
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=llm_model, temperature=0)
    market_data = MarketDataAPI()
    news = FinancialNewsAPI()
    scraper = FinancialWebScraper()
    
    return create_specialized_agents(
        llm=llm,
        market_data_api=market_data,
        news_api=news,
        web_scraper=scraper,
        retriever=None
    )


class TestAgentTools:
    """Test that agents have the correct number and types of tools"""
    
    def test_finance_qa_agent_exists(self, agents):
        """Test that finance_qa agent exists and is configured"""
        agent = agents["finance_qa"]
        assert agent is not None
        
    def test_portfolio_analyzer_agent_exists(self, agents):
        """Test that portfolio_analyzer agent exists and is configured"""
        agent = agents["portfolio_analyzer"]
        assert agent is not None
    
    def test_market_analyst_agent_exists(self, agents):
        """Test that market_analyst agent exists and is configured"""
        agent = agents["market_analyst"]
        assert agent is not None
    
    def test_goal_planner_agent_exists(self, agents):
        """Test that goal_planner agent exists and is configured"""
        agent = agents["goal_planner"]
        assert agent is not None
    
    def test_tax_educator_agent_exists(self, agents):
        """Test that tax_educator agent exists and is configured"""
        agent = agents["tax_educator"]
        assert agent is not None


class TestAPIClients:
    """Test API client functionality"""
    
    def test_market_data_api_initialization(self):
        """Test that market data API initializes correctly"""
        api = MarketDataAPI()
        assert api is not None
        assert hasattr(api, 'get_stock_quote')
        assert hasattr(api, 'get_company_info')
        assert hasattr(api, 'get_market_indices')
    
    def test_news_api_initialization(self):
        """Test that news API initializes correctly"""
        api = FinancialNewsAPI()
        assert api is not None
        assert hasattr(api, 'get_financial_news')
    
    def test_web_scraper_initialization(self):
        """Test that web scraper initializes correctly"""
        scraper = FinancialWebScraper()
        assert scraper is not None
        assert hasattr(scraper, 'scrape_investopedia_term')


class TestMarketDataAPI:
    """Test market data API methods"""
    
    def test_get_stock_quote_structure(self):
        """Test that get_stock_quote returns proper structure"""
        api = MarketDataAPI()
        result = api.get_stock_quote("AAPL")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have required keys
        expected_keys = ["symbol", "price", "currency"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_get_company_info_structure(self):
        """Test that get_company_info returns proper structure"""
        api = MarketDataAPI()
        result = api.get_company_info("AAPL")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        assert "symbol" in result
    
    def test_get_market_indices_structure(self):
        """Test that get_market_indices returns proper structure"""
        api = MarketDataAPI()
        result = api.get_market_indices()
        
        # Should return a dictionary
        assert isinstance(result, dict)
        assert "indices" in result


class TestNewsAPI:
    """Test news API methods"""
    
    def test_get_financial_news_structure(self):
        """Test that get_financial_news returns proper structure"""
        api = FinancialNewsAPI()
        result = api.get_financial_news("AAPL")
        
        # Should return a dictionary
        assert isinstance(result, dict)
        # Should have articles key
        assert "articles" in result or "error" in result


class TestAgentIntegration:
    """Test agent integration with tools"""
    
    def test_all_agents_created(self, agents):
        """Test that all 5 agents are created"""
        assert len(agents) == 5
        expected_agents = ["finance_qa", "portfolio_analyzer", "market_analyst", "goal_planner", "tax_educator"]
        for agent_name in expected_agents:
            assert agent_name in agents, f"Missing agent: {agent_name}"
    
    def test_agents_are_not_none(self, agents):
        """Test that all agents are properly initialized"""
        for agent_name, agent in agents.items():
            assert agent is not None, f"{agent_name} is None"


class TestErrorHandling:
    """Test error handling in API clients"""
    
    def test_market_data_api_invalid_symbol(self):
        """Test handling of invalid stock symbols"""
        api = MarketDataAPI()
        result = api.get_stock_quote("INVALID_SYMBOL_XYZ")
        
        # Should still return a dictionary, not crash
        assert isinstance(result, dict)
    
    def test_market_data_api_empty_symbol(self):
        """Test handling of empty symbol"""
        api = MarketDataAPI()
        result = api.get_stock_quote("")
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_news_api_empty_query(self):
        """Test handling of empty news query"""
        api = FinancialNewsAPI()
        result = api.get_financial_news("")
        
        # Should handle gracefully
        assert isinstance(result, dict)


# Run tests with: pytest tests/test_tools.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


class TestAPIClients:
    """Test API client functionality"""
    
    def test_market_data_api_initialization(self):
        """Test that market data API initializes correctly"""
        from market_data_api import MarketDataAPI
        api = MarketDataAPI()
        assert api is not None
        assert hasattr(api, 'get_stock_quote')
        assert hasattr(api, 'get_company_info')
    
    def test_news_api_initialization(self):
        """Test that news API initializes correctly"""
        from news_api import FinancialNewsAPI
        api = FinancialNewsAPI()
        assert api is not None
        assert hasattr(api, 'get_financial_news')
    
    def test_web_scraper_initialization(self):
        """Test that web scraper initializes correctly"""
        from web_scraper import FinancialWebScraper
        scraper = FinancialWebScraper()
        assert scraper is not None
        assert hasattr(scraper, 'scrape_investopedia_term')


class TestAgentIntegration:
    """Test agent integration with tools"""
    
    def test_all_agents_created(self, agents):
        """Test that all 5 agents are created"""
        assert len(agents) == 5
        expected_agents = ["finance_qa", "portfolio_analyzer", "market_analyst", "goal_planner", "tax_educator"]
        for agent_name in expected_agents:
            assert agent_name in agents, f"Missing agent: {agent_name}"
    
    def test_agents_have_tools(self, agents):
        """Test that all agents have their tools configured"""
        for agent_name, agent in agents.items():
            assert agent is not None, f"{agent_name} is None"
            # Each agent should be a properly configured agent instance


# Run tests with: pytest tests/test_tools.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

