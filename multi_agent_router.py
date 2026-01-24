"""
Multi-Agent Router for AI Finance Assistant
Routes user queries to the most appropriate specialized agent(s).
"""

import logging
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class QueryRouter:
    """Routes queries to appropriate specialized agents."""
    
    # Agent descriptions for routing decisions
    AGENT_DESCRIPTIONS = {
        "finance_qa": """
            Finance Q&A Agent - Handles general financial education questions:
            - Financial terminology and definitions
            - Basic investment concepts (stocks, bonds, ETFs, mutual funds)
            - How financial products work
            - General "what is" or "explain" questions
            - Educational resources
            Examples: "What is diversification?", "Explain compound interest", "How do ETFs work?"
        """,
        "portfolio_analyzer": """
            Portfolio Analyzer Agent - Analyzes investment portfolios:
            - Portfolio composition and allocation analysis
            - Asset diversification assessment
            - Sector concentration analysis
            - Portfolio performance review
            - When user provides list of holdings/stocks
            Examples: "Analyze my portfolio", "Check my diversification", "Review these holdings: AAPL, MSFT, GOOGL"
        """,
        "market_analyst": """
            Market Analyst Agent - Provides market data and stock information:
            - Real-time stock quotes and prices
            - Company information and fundamentals
            - Market indices (S&P 500, Dow, NASDAQ)
            - Stock news and market updates
            - Historical price data
            Examples: "What's Apple's stock price?", "Show me market indices", "News about Tesla"
        """,
        "goal_planner": """
            Goal Planner Agent - Helps with financial planning and goals:
            - Retirement savings calculations
            - Financial goal planning (house, education, etc.)
            - Required savings calculations
            - Timeline and contribution planning
            - "How much do I need" questions
            Examples: "Plan my retirement", "How much to save for $50k in 5 years?", "Retirement calculator"
        """,
        "tax_educator": """
            Tax Educator Agent - Explains tax concepts and strategies:
            - Retirement account types (IRA, 401k, Roth IRA, HSA)
            - Capital gains tax (short-term vs long-term)
            - Tax-loss harvesting
            - Tax implications of investments
            - Account comparisons
            Examples: "IRA vs Roth IRA", "Explain capital gains tax", "Tax-loss harvesting"
        """
    }
    
    def __init__(self, llm: ChatOpenAI):
        """Initialize the query router."""
        self.llm = llm
        logger.info("QueryRouter initialized")
    
    def route_query(self, query: str) -> List[str]:
        """
        Route a query to the most appropriate agent(s).
        
        Args:
            query: User's query string
            
        Returns:
            List of agent names to handle the query (usually 1, sometimes 2-3)
        """
        logger.info(f"Routing query: {query[:100]}...")
        
        # Create routing prompt
        agents_info = "\n\n".join([
            f"**{name}**: {desc.strip()}"
            for name, desc in self.AGENT_DESCRIPTIONS.items()
        ])
        
        system_prompt = f"""You are a query routing expert for a financial AI assistant system.
Your job is to analyze user queries and determine which specialized agent(s) should handle them.

Available Agents:
{agents_info}

Instructions:
1. Analyze the user's query carefully
2. Select the MOST appropriate agent(s) to handle it
3. Usually select ONE agent, but you can select 2-3 if the query requires multiple specialties
4. Return ONLY the agent names separated by commas (e.g., "market_analyst" or "portfolio_analyzer,market_analyst")
5. Valid agent names: finance_qa, portfolio_analyzer, market_analyst, goal_planner, tax_educator

Examples:
Query: "What is a diversified portfolio?"
Response: finance_qa

Query: "What's the current price of Apple stock?"
Response: market_analyst

Query: "I have AAPL, MSFT, GOOGL in my portfolio. Analyze it."
Response: portfolio_analyzer,market_analyst

Query: "I'm 30 and want to retire at 65. How much should I save?"
Response: goal_planner

Query: "Should I use a Traditional IRA or Roth IRA?"
Response: tax_educator

Query: "What's Tesla's stock price and should I buy it?"
Response: market_analyst,finance_qa

Now route the following query:"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            routing_result = response.content.strip().lower()
            
            # Parse agent names
            agent_names = [name.strip() for name in routing_result.split(',')]
            
            # Validate agent names
            valid_agents = [
                name for name in agent_names
                if name in self.AGENT_DESCRIPTIONS
            ]
            
            if not valid_agents:
                logger.warning(f"No valid agents found in routing result: {routing_result}")
                # Default to finance_qa for general questions
                valid_agents = ["finance_qa"]
            
            logger.info(f"✅ Routed to agents: {', '.join(valid_agents)}")
            return valid_agents
            
        except Exception as e:
            logger.error(f"❌ Error routing query: {e}")
            # Default to finance_qa on error
            return ["finance_qa"]
    
    def explain_routing(self, query: str, agents: List[str]) -> str:
        """
        Provide a brief explanation of why the query was routed to specific agents.
        
        Args:
            query: User's query
            agents: List of agent names
            
        Returns:
            Human-readable explanation
        """
        agent_map = {
            "finance_qa": "Finance Q&A (general education)",
            "portfolio_analyzer": "Portfolio Analyzer (investment analysis)",
            "market_analyst": "Market Analyst (real-time data)",
            "goal_planner": "Goal Planner (financial planning)",
            "tax_educator": "Tax Educator (tax concepts)"
        }
        
        agent_names = [agent_map.get(a, a) for a in agents]
        
        if len(agents) == 1:
            return f"Routing to: **{agent_names[0]}**"
        else:
            return f"Routing to: **{', '.join(agent_names)}**"


def create_router(llm: ChatOpenAI) -> QueryRouter:
    """
    Factory function to create a query router.
    
    Args:
        llm: Language model to use for routing decisions
        
    Returns:
        QueryRouter instance
    """
    return QueryRouter(llm)
