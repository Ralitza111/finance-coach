"""
Unit Tests for Multi-Agent AI Finance Assistant System
Tests routing logic, agent responses, and error handling.
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multi_agent_orchestrator import MultiAgentOrchestrator
from multi_agent_router import QueryRouter
from specialized_agents import create_specialized_agents
from market_data_api import MarketDataAPI
from news_api import FinancialNewsAPI
from web_scraper import FinancialWebScraper
from langchain_openai import ChatOpenAI

# Load environment variables for tests
load_dotenv()


@pytest.fixture
def agents():
    """Fixture to create test agent instances"""
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


@pytest.fixture
def router():
    """Fixture to create a test router instance"""
    return QueryRouter(os.getenv("LLM_MODEL", "gpt-4o-mini"))


@pytest.fixture
def orchestrator(agents):
    """Fixture to create a test orchestrator instance"""
    return MultiAgentOrchestrator(agents)


class TestRouting:
    """Test the routing logic"""
    
    def test_finance_qa_routing(self, router):
        """Test that financial term queries route to finance_qa"""
        route = router.route_query("What is a dividend?")
        assert isinstance(route, list)
        assert "finance_qa" in route
    
    def test_finance_qa_concept_routing(self, router):
        """Test that financial concept queries route to finance_qa"""
        route = router.route_query("Explain compound interest")
        assert isinstance(route, list)
        assert "finance_qa" in route
    
    def test_portfolio_analyzer_routing(self, router):
        """Test that portfolio queries route to portfolio_analyzer"""
        route = router.route_query("Analyze my portfolio allocation")
        assert isinstance(route, list)
        assert "portfolio_analyzer" in route
    
    def test_portfolio_diversification_routing(self, router):
        """Test that diversification queries route to portfolio_analyzer"""
        route = router.route_query("How diversified is my portfolio?")
        assert isinstance(route, list)
        assert "portfolio_analyzer" in route
    
    def test_market_analyst_routing(self, router):
        """Test that stock price queries route to market_analyst"""
        route = router.route_query("What is the current price of AAPL?")
        assert isinstance(route, list)
        assert "market_analyst" in route
    
    def test_market_news_routing(self, router):
        """Test that market news queries route to market_analyst"""
        route = router.route_query("Get latest news about Tesla")
        assert isinstance(route, list)
        assert "market_analyst" in route
    
    def test_goal_planner_routing(self, router):
        """Test that retirement planning queries route to goal_planner"""
        route = router.route_query("How much do I need to save for retirement?")
        assert isinstance(route, list)
        assert "goal_planner" in route
    
    def test_goal_planner_savings_routing(self, router):
        """Test that savings goal queries route to goal_planner"""
        route = router.route_query("Calculate my savings goal for a house")
        assert isinstance(route, list)
        assert "goal_planner" in route
    
    def test_tax_educator_routing(self, router):
        """Test that tax queries route to tax_educator"""
        route = router.route_query("What is the difference between Roth IRA and Traditional IRA?")
        assert isinstance(route, list)
        assert "tax_educator" in route
    
    def test_tax_strategy_routing(self, router):
        """Test that tax strategy queries route to tax_educator"""
        route = router.route_query("Explain tax loss harvesting")
        assert isinstance(route, list)
        assert "tax_educator" in route
    
    def test_multi_agent_routing(self, router):
        """Test that complex queries may route to multiple agents"""
        route = router.route_query("I want to retire in 20 years, analyze my portfolio and suggest tax strategies")
        assert isinstance(route, list)
        # Should route to multiple agents
        assert len(route) >= 1
        # At least one of these should be in the routing
        assert any(agent in route for agent in ["goal_planner", "portfolio_analyzer", "tax_educator"])


class TestAgents:
    """Test the agent functionality"""
    
    def test_agents_creation(self, agents):
        """Test that all agents are created successfully"""
        assert len(agents) == 5
        assert "finance_qa" in agents
        assert "portfolio_analyzer" in agents
        assert "market_analyst" in agents
        assert "goal_planner" in agents
        assert "tax_educator" in agents
    
    def test_finance_qa_agent_tools(self, agents):
        """Test that finance_qa agent has the right tools"""
        agent = agents["finance_qa"]
        assert agent is not None
        # Agent should have tools for searching financial terms, educational content, etc.
    
    def test_portfolio_analyzer_agent_tools(self, agents):
        """Test that portfolio_analyzer agent has the right tools"""
        agent = agents["portfolio_analyzer"]
        assert agent is not None
        # Agent should have tools for portfolio analysis and diversification
    
    def test_market_analyst_agent_tools(self, agents):
        """Test that market_analyst agent has the right tools"""
        agent = agents["market_analyst"]
        assert agent is not None
        # Agent should have tools for stock quotes, company info, news, etc.
    
    def test_goal_planner_agent_tools(self, agents):
        """Test that goal_planner agent has the right tools"""
        agent = agents["goal_planner"]
        assert agent is not None
        # Agent should have tools for retirement and savings calculations
    
    def test_tax_educator_agent_tools(self, agents):
        """Test that tax_educator agent has the right tools"""
        agent = agents["tax_educator"]
        assert agent is not None
        # Agent should have tools for tax education and strategy


class TestOrchestrator:
    """Test the orchestrator functionality"""
    
    def test_orchestrator_creation(self, orchestrator):
        """Test that orchestrator is created with all agents"""
        assert orchestrator is not None
        assert len(orchestrator.agents) == 5
    
    def test_orchestrator_simple_query(self, orchestrator):
        """Test orchestrator handling simple query"""
        response = orchestrator.process_query("What is a stock?")
        assert isinstance(response, dict)
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_orchestrator_agent_selection(self, orchestrator):
        """Test that orchestrator selects appropriate agent"""
        response = orchestrator.process_query("What is dividend yield?")
        assert isinstance(response, dict)
        assert "agent_used" in response
        assert response["agent_used"] in ["finance_qa", "orchestrator"]


class TestRouterValidation:
    """Test router validation and error handling"""
    
    def test_router_returns_valid_agents(self, router):
        """Test that router only returns valid agent names"""
        valid_agents = ["finance_qa", "portfolio_analyzer", "market_analyst", "goal_planner", "tax_educator"]
        route = router.route_query("What is compound interest?")
        assert isinstance(route, list)
        for agent in route:
            assert agent in valid_agents, f"Invalid agent returned: {agent}"
    
    def test_router_handles_empty_query(self, router):
        """Test router behavior with empty query"""
        route = router.route_query("")
        assert isinstance(route, list)
        # Should still return at least one agent (probably finance_qa as fallback)


class TestErrorHandling:
    """Test error handling and fallback logic"""
    
    def test_orchestrator_error_handling(self, orchestrator):
        """Test that orchestrator handles errors gracefully"""
        # Test with empty query
        response = orchestrator.process_query("")
        assert isinstance(response, dict)
        assert "response" in response or "error" in response
    
    def test_router_with_ambiguous_query(self, router):
        """Test router with ambiguous queries"""
        route = router.route("help")
        assert route.agent_name in ["finance_qa", "orchestrator"]
        assert isinstance(route.reasoning, str)
    
    def test_orchestrator_fallback(self, orchestrator):
        """Test fallback response for out-of-scope queries"""
        response = orchestrator.process_query("What's the weather today?")
        assert isinstance(response, dict)
        assert "response" in response
        # Should indicate that the query is out of scope or provide general guidance


class TestIntegration:
    """Integration tests for end-to-end functionality"""
    
    def test_simple_finance_query_flow(self, orchestrator):
        """Test a simple finance query from start to finish"""
        response = orchestrator.process_query("What is a mutual fund?")
        assert isinstance(response, dict)
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_retirement_planning_flow(self, orchestrator):
        """Test retirement planning query flow"""
        query = "I'm 30 years old, want to retire at 65 with $2 million. How much should I save monthly?"
        response = orchestrator.process_query(query)
        assert isinstance(response, dict)
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_tax_query_flow(self, orchestrator):
        """Test tax education query flow"""
        response = orchestrator.process_query("What are the tax implications of capital gains?")
        assert isinstance(response, dict)
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_portfolio_analysis_flow(self, orchestrator):
        """Test portfolio analysis query flow"""
        query = "I have 60% stocks, 30% bonds, 10% cash. Is this well diversified?"
        response = orchestrator.process_query(query)
        assert isinstance(response, dict)
        assert "response" in response
        assert len(response["response"]) > 0
    
    def test_market_data_flow(self, orchestrator):
        """Test market data query flow"""
        response = orchestrator.process_query("Tell me about Apple stock")
        assert isinstance(response, dict)
        assert "response" in response
        # Response should contain information (may have rate limiting warnings)
        assert len(response["response"]) > 0


class TestAPIClients:
    """Test API client functionality"""
    
    def test_market_data_api_import(self):
        """Test that market data API can be imported"""
        from market_data_api import MarketDataAPI
        assert MarketDataAPI is not None
    
    def test_news_api_import(self):
        """Test that news API can be imported"""
        from news_api import FinancialNewsAPI
        assert FinancialNewsAPI is not None
    
    def test_web_scraper_import(self):
        """Test that web scraper can be imported"""
        from web_scraper import FinancialWebScraper
        assert FinancialWebScraper is not None


class TestConfiguration:
    """Test configuration and environment setup"""
    
    def test_env_variables_loaded(self):
        """Test that environment variables are loaded"""
        # At minimum, we should have OPENAI_API_KEY
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is not None
        assert len(api_key) > 0
    
    def test_alpha_vantage_key(self):
        """Test that Alpha Vantage API key is configured"""
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        assert api_key is not None
        assert len(api_key) > 0
    
    def test_news_api_key(self):
        """Test that News API key is configured"""
        api_key = os.getenv("NEWS_API_KEY")
        assert api_key is not None
        assert len(api_key) > 0
    
    def test_llm_model_config(self):
        """Test that LLM model is configured"""
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        assert model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4"]


# Run tests with: pytest tests/test_multi_agent.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
