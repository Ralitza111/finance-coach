"""
Multi-Agent Router for AI Finance Assistant
Routes user queries to the most appropriate specialized agent(s).
Uses LLM-based task planning with reasoning for intelligent routing.
"""

import logging
from typing import Dict, List, Tuple, Union
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
    
    def route_query(self, query: str, explain: bool = False) -> Tuple[List[str], str]:
        """
        Route a query to the most appropriate agent(s) using LLM-based task planning.
        
        Args:
            query: User's query string
            explain: Whether to return reasoning (default: False for compatibility)
            
        Returns:
            Tuple of (List of agent names, reasoning explanation)
        """
        logger.info(f"Routing query: {query[:100]}...")
        
        # Create routing prompt with reasoning
        agents_info = "\n\n".join([
            f"**{name}**: {desc.strip()}"
            for name, desc in self.AGENT_DESCRIPTIONS.items()
        ])
        
        system_prompt = f"""You are an intelligent query routing system for a financial AI assistant.
You use LLM-based task planning to determine the optimal agent(s) for each query.

Available Agents:
{agents_info}

Instructions:
1. Analyze the user's query to understand their intent and information needs
2. Use task decomposition - break complex queries into component tasks
3. Select the MOST appropriate agent(s) to handle each task
4. Usually select ONE agent, but select 2-3 if the query requires multiple specialties
5. Provide your reasoning for the selection

Response Format:
AGENTS: [comma-separated agent names]
REASONING: [brief explanation of why these agents were selected]

Valid agent names: finance_qa, portfolio_analyzer, market_analyst, goal_planner, tax_educator

Examples:

Query: "What is a diversified portfolio?"
AGENTS: finance_qa
REASONING: This is a definitional question about a financial concept, best handled by the educational agent.

Query: "What's the current price of Apple stock?"
AGENTS: market_analyst
REASONING: Requires real-time market data retrieval.

Query: "I have AAPL, MSFT, GOOGL in my portfolio. Should I invest more?"
AGENTS: portfolio_analyzer,market_analyst
REASONING: Needs portfolio analysis to assess current holdings AND market data for informed recommendations.

Query: "I'm 30 and want to retire at 65. How much should I save?"
AGENTS: goal_planner
REASONING: Retirement planning calculation requiring goal-based financial planning.

Query: "Should I use a Traditional IRA or Roth IRA?"
AGENTS: tax_educator
REASONING: Tax-advantaged account comparison requiring tax education expertise.

Query: "What's Tesla's stock price and is it a good investment for me?"
AGENTS: market_analyst,finance_qa
REASONING: Needs current market data (price) AND educational context about investment evaluation principles.

Now route the following query:"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            routing_result = response.content.strip()
            
            # Parse AGENTS and REASONING
            agents_line = ""
            reasoning_line = ""
            
            for line in routing_result.split('\n'):
                if line.startswith('AGENTS:'):
                    agents_line = line.replace('AGENTS:', '').strip()
                elif line.startswith('REASONING:'):
                    reasoning_line = line.replace('REASONING:', '').strip()
            
            # Fallback parsing if format not followed
            if not agents_line:
                # Try to extract agent names from any format
                agents_line = routing_result.lower().split('\n')[0]
            
            # Parse agent names
            agent_names = [name.strip() for name in agents_line.lower().split(',')]
            
            # Validate agent names
            valid_agents = [
                name for name in agent_names
                if name in self.AGENT_DESCRIPTIONS
            ]
            
            if not valid_agents:
                logger.warning(f"No valid agents found in routing result: {routing_result}")
                # Default to finance_qa for general questions
                valid_agents = ["finance_qa"]
                reasoning_line = "Defaulting to general financial education for this query."
            
            logger.info(f"✅ Routed to agents: {', '.join(valid_agents)}")
            if reasoning_line:
                logger.info(f"💡 Reasoning: {reasoning_line}")
            
            return valid_agents if not explain else (valid_agents, reasoning_line)
            
        except Exception as e:
            logger.error(f"❌ Error routing query: {e}")
            # Default to finance_qa on error
            reasoning = "Error in routing - defaulting to general education"
            return ["finance_qa"] if not explain else (["finance_qa"], reasoning)
    
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
