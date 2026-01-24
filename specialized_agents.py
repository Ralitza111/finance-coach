"""
Specialized Agents for AI Finance Assistant Multi-Agent System
Each agent is an expert in a specific financial domain with specialized tools.
"""

import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

# Setup logging
logger = logging.getLogger(__name__)


class BaseFinanceAgent:
    """Base class for all specialized finance agents."""
    
    def __init__(self, llm: ChatOpenAI, tools: List, system_prompt: str, name: str):
        self.name = name
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.memory = MemorySaver()
        logger.info(f"Initializing {name} agent with {len(tools)} tools")
        self.agent = create_react_agent(
            llm,
            tools,
            checkpointer=self.memory
        )
    
    def invoke(self, query: str, thread_id: str = "default") -> str:
        """Invoke the agent with a query."""
        logger.debug(f"{self.name} invoked with query: {query[:100]}...")
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Add system prompt as first message
            messages = [
                SystemMessage(content=self.system_prompt),
                ("user", query)
            ]
            
            response = self.agent.invoke(
                {"messages": messages},
                config=config
            )
            
            # Extract the final response
            messages = response.get("messages", [])
            if messages:
                result = messages[-1].content
                logger.debug(f"{self.name} generated response of length {len(result)}")
                return result
            
            logger.warning(f"{self.name} generated no response")
            return "No response generated."
            
        except Exception as e:
            logger.error(f"{self.name} invoke failed: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "tool_count": len(self.tools),
            "tools": [tool.name for tool in self.tools]
        }


class FinanceQAAgent(BaseFinanceAgent):
    """
    💬 Specialized agent for general financial education and Q&A.
    
    Expertise:
    - Financial terminology and concepts
    - Investment basics
    - General financial advice
    - Educational content
    - Financial product explanations
    """
    
    def __init__(self, llm: ChatOpenAI, finance_tools: List):
        system_prompt = """You are the Finance Q&A Agent, an expert financial educator who helps people understand financial concepts, terminology, and basic investment principles.

Your expertise:
- Explaining financial terms and concepts in simple language
- Teaching investment basics (stocks, bonds, ETFs, mutual funds)
- Answering questions about financial products
- Providing educational resources
- Breaking down complex financial topics

Your communication style:
- Clear and jargon-free explanations
- Patient and encouraging
- Use analogies and examples
- Always educational, never prescriptive
- Include disclaimers that you're providing education, not financial advice

Important guidelines:
- You educate but DO NOT provide personalized financial advice
- Always suggest consulting with licensed financial advisors for specific situations
- Focus on general principles and education
- Encourage continued learning

When users ask questions, start with clear definitions, then provide context and examples."""

        super().__init__(llm, finance_tools, system_prompt, "Finance Q&A Agent")


class PortfolioAnalyzerAgent(BaseFinanceAgent):
    """
    📊 Specialized agent for analyzing investment portfolios.
    
    Expertise:
    - Portfolio composition analysis
    - Asset allocation review
    - Diversification assessment
    - Risk analysis
    - Performance metrics
    """
    
    def __init__(self, llm: ChatOpenAI, portfolio_tools: List):
        system_prompt = """You are the Portfolio Analyzer Agent, an expert at analyzing investment portfolios and providing insights on asset allocation, diversification, and risk.

Your expertise:
- Analyzing portfolio composition and asset allocation
- Assessing diversification across sectors and asset classes
- Identifying concentration risks
- Calculating key metrics (expense ratios, yield, etc.)
- Comparing portfolios to benchmarks

Your communication style:
- Data-driven and analytical
- Visual and clear presentations
- Highlight both strengths and areas for improvement
- Provide actionable insights
- Use percentages and metrics effectively

Analysis approach:
1. Start with overall portfolio composition
2. Examine asset allocation
3. Check diversification
4. Identify concentration risks
5. Suggest areas for consideration

Always remind users that this is educational analysis, not personalized investment advice."""

        super().__init__(llm, portfolio_tools, system_prompt, "Portfolio Analyzer Agent")


class MarketAnalystAgent(BaseFinanceAgent):
    """
    📈 Specialized agent for market data, trends, and stock analysis.
    
    Expertise:
    - Real-time stock quotes
    - Market indices tracking
    - Company information
    - Historical data analysis
    - Market trend identification
    """
    
    def __init__(self, llm: ChatOpenAI, market_tools: List):
        system_prompt = """You are the Market Analyst Agent, an expert at providing real-time market data, analyzing stocks, and explaining market trends.

Your expertise:
- Fetching and interpreting real-time stock quotes
- Analyzing company fundamentals
- Tracking market indices (S&P 500, Dow, NASDAQ)
- Providing historical price context
- Explaining market movements

Your communication style:
- Timely and data-focused
- Present numbers clearly with context
- Explain what metrics mean
- Highlight important trends
- Neutral and objective

When presenting stock data:
1. Show current price and change
2. Provide relevant context (52-week range, P/E ratio, etc.)
3. Include company basics (sector, market cap)
4. Note any significant news or events
5. Explain what the data means for investors

Remember: You provide data and education, NOT buy/sell recommendations."""

        super().__init__(llm, market_tools, system_prompt, "Market Analyst Agent")


class GoalPlannerAgent(BaseFinanceAgent):
    """
    🎯 Specialized agent for financial goal setting and planning.
    
    Expertise:
    - Goal setting frameworks
    - Retirement planning
    - Savings strategies
    - Risk tolerance assessment
    - Timeline planning
    """
    
    def __init__(self, llm: ChatOpenAI, planning_tools: List):
        system_prompt = """You are the Goal Planner Agent, an expert at helping people set and plan for their financial goals using structured frameworks and calculations.

Your expertise:
- Setting SMART financial goals
- Retirement planning and calculations
- Emergency fund planning
- Major purchase planning (house, education, etc.)
- Risk tolerance assessment
- Timeline development

Your communication style:
- Encouraging and motivational
- Break down big goals into steps
- Use specific numbers and timeframes
- Realistic and practical
- Focus on action steps

Your planning approach:
1. Understand the user's goal and timeline
2. Assess current financial situation
3. Calculate required savings/contributions
4. Consider risk tolerance
5. Create actionable steps
6. Address potential obstacles

Always emphasize:
- Start where they are
- Consistency matters more than perfection
- Adjust plans as life changes
- Regular review and rebalancing

You guide planning, but recommend professional advisors for detailed financial plans."""

        super().__init__(llm, planning_tools, system_prompt, "Goal Planner Agent")


class TaxEducatorAgent(BaseFinanceAgent):
    """
    💰 Specialized agent for tax education and account types.
    
    Expertise:
    - Tax-advantaged accounts (401k, IRA, Roth IRA, HSA)
    - Capital gains tax basics
    - Tax-loss harvesting concepts
    - Account type comparisons
    - Tax implications of investments
    """
    
    def __init__(self, llm: ChatOpenAI, tax_tools: List):
        system_prompt = """You are the Tax Educator Agent, an expert at explaining tax concepts, account types, and tax-advantaged investing strategies in clear, understandable terms.

Your expertise:
- Tax-advantaged retirement accounts (Traditional IRA, Roth IRA, 401k, 403b)
- Health Savings Accounts (HSAs)
- Taxable investment accounts
- Capital gains tax (short-term vs long-term)
- Tax-loss harvesting concepts
- Required Minimum Distributions (RMDs)

Your communication style:
- Break down complex tax rules into simple concepts
- Use clear comparisons and examples
- Highlight key differences between account types
- Focus on general principles
- Acknowledge complexity where it exists

Teaching approach:
1. Start with the basics
2. Compare and contrast options
3. Use specific examples with numbers
4. Explain trade-offs
5. Highlight common mistakes to avoid

Critical reminders:
- You provide tax EDUCATION, not tax advice
- Tax laws change frequently
- Individual situations vary greatly
- Always recommend consulting a tax professional or CPA for specific situations
- Emphasize the importance of understanding their personal tax situation

You help people understand concepts so they can have informed conversations with their tax advisors."""

        super().__init__(llm, tax_tools, system_prompt, "Tax Educator Agent")


def create_specialized_agents(
    llm: ChatOpenAI,
    market_data_api,
    news_api,
    web_scraper,
    retriever=None
) -> Dict[str, BaseFinanceAgent]:
    """
    Create all specialized finance agents with their respective tools.
    
    Args:
        llm: Language model to use
        market_data_api: Market data API instance
        news_api: Financial news API instance
        web_scraper: Web scraper instance
        retriever: Knowledge base retriever (optional)
        
    Returns:
        Dictionary mapping agent names to agent instances
    """
    
    # Define tools for Finance Q&A Agent
    @tool
    def search_financial_term(term: str) -> str:
        """Search for the definition and explanation of a financial term."""
        try:
            result = web_scraper.scrape_investopedia_term(term)
            if result:
                return f"**{result['title']}**\n\n{result['definition']}\n\nSource: {result['source']}"
            return f"Could not find definition for '{term}'. Try a different term or rephrasing."
        except Exception as e:
            return f"Error searching for term: {str(e)}"
    
    @tool
    def get_educational_content(topic: str) -> str:
        """Get educational articles and resources on a financial topic."""
        try:
            content = web_scraper.get_financial_education_content(topic, limit=3)
            if content:
                result = f"Educational resources on {topic}:\n\n"
                for idx, item in enumerate(content, 1):
                    result += f"{idx}. **{item['title']}**\n"
                    result += f"   {item['description']}\n"
                    result += f"   Source: {item['source']}\n\n"
                return result
            return f"No educational content found for '{topic}'."
        except Exception as e:
            return f"Error fetching educational content: {str(e)}"
    
    @tool
    def explain_financial_calculator(calculator_type: str) -> str:
        """Get information about financial calculators (compound_interest, retirement, mortgage)."""
        try:
            calc_data = web_scraper.get_financial_calculator_data(calculator_type)
            if 'formula' in calc_data:
                result = f"**{calc_data['name']}**\n\n"
                result += f"Description: {calc_data['description']}\n\n"
                result += f"Formula: {calc_data['formula']}\n\n"
                result += f"Parameters: {', '.join(calc_data['parameters'])}"
                return result
            return f"Calculator type '{calculator_type}' not found."
        except Exception as e:
            return f"Error getting calculator info: {str(e)}"
    
    finance_qa_tools = [search_financial_term, get_educational_content, explain_financial_calculator]
    
    # Define tools for Portfolio Analyzer Agent
    @tool
    def analyze_portfolio_allocation(portfolio_json: str) -> str:
        """Analyze asset allocation of a portfolio. Expects JSON with holdings: [{"symbol": "AAPL", "shares": 10}, ...]"""
        try:
            import json
            portfolio = json.loads(portfolio_json)
            
            total_value = 0
            holdings_data = []
            
            for holding in portfolio:
                symbol = holding['symbol']
                shares = float(holding['shares'])
                quote = market_data_api.get_stock_quote(symbol)
                
                if quote:
                    value = quote['price'] * shares
                    total_value += value
                    holdings_data.append({
                        'symbol': symbol,
                        'shares': shares,
                        'price': quote['price'],
                        'value': value,
                        'name': quote['name']
                    })
            
            if total_value == 0:
                return "Could not calculate portfolio value."
            
            result = f"**Portfolio Analysis**\n\nTotal Value: ${total_value:,.2f}\n\n**Holdings:**\n"
            for holding in holdings_data:
                allocation = (holding['value'] / total_value) * 100
                result += f"- {holding['symbol']} ({holding['name']}): {holding['shares']} shares @ ${holding['price']:.2f} = ${holding['value']:,.2f} ({allocation:.1f}%)\n"
            
            return result
        except Exception as e:
            return f"Error analyzing portfolio: {str(e)}"
    
    @tool
    def check_portfolio_diversification(symbols_list: str) -> str:
        """Check diversification across sectors. Expects comma-separated symbols (e.g., 'AAPL,MSFT,JPM')."""
        try:
            symbols = [s.strip().upper() for s in symbols_list.split(',')]
            sectors = {}
            
            for symbol in symbols:
                info = market_data_api.get_company_info(symbol)
                if info and info['sector'] != 'N/A':
                    sector = info['sector']
                    sectors[sector] = sectors.get(sector, 0) + 1
            
            if not sectors:
                return "Could not determine sector diversification."
            
            result = "**Sector Diversification:**\n\n"
            for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(symbols)) * 100
                result += f"- {sector}: {count} stocks ({percentage:.1f}%)\n"
            
            return result
        except Exception as e:
            return f"Error checking diversification: {str(e)}"
    
    portfolio_analyzer_tools = [analyze_portfolio_allocation, check_portfolio_diversification]
    
    # Define tools for Market Analyst Agent
    @tool
    def get_stock_quote(symbol: str) -> str:
        """Get real-time stock quote for a ticker symbol."""
        try:
            quote = market_data_api.get_stock_quote(symbol)
            if quote:
                result = f"**{quote['name']} ({quote['symbol']})**\n\n"
                result += f"Price: ${quote['price']:.2f}\n"
                result += f"Change: ${quote['change']:.2f} ({quote['change_percent']:.2f}%)\n"
                result += f"Open: ${quote['open']:.2f} | High: ${quote['high']:.2f} | Low: ${quote['low']:.2f}\n"
                result += f"Volume: {quote['volume']:,}\n"
                if quote['market_cap'] != 'N/A':
                    result += f"Market Cap: ${quote['market_cap']:,}\n"
                if quote['pe_ratio'] != 'N/A':
                    result += f"P/E Ratio: {quote['pe_ratio']:.2f}\n"
                result += f"\nUpdated: {quote['timestamp']}"
                return result
            return f"Could not fetch quote for {symbol}."
        except Exception as e:
            return f"Error fetching stock quote: {str(e)}"
    
    @tool
    def get_company_information(symbol: str) -> str:
        """Get detailed company information including sector, industry, and description."""
        try:
            info = market_data_api.get_company_info(symbol)
            if info:
                result = f"**{info['name']} ({info['symbol']})**\n\n"
                result += f"Sector: {info['sector']}\n"
                result += f"Industry: {info['industry']}\n\n"
                if info['description'] != 'N/A':
                    result += f"Description: {info['description'][:300]}...\n\n"
                result += f"Market Cap: ${info['market_cap']:,}\n" if info['market_cap'] != 'N/A' else ""
                result += f"P/E Ratio: {info['pe_ratio']}\n" if info['pe_ratio'] != 'N/A' else ""
                result += f"Dividend Yield: {info['dividend_yield']}\n" if info['dividend_yield'] != 'N/A' else ""
                return result
            return f"Could not fetch company info for {symbol}."
        except Exception as e:
            return f"Error fetching company information: {str(e)}"
    
    @tool
    def get_market_indices() -> str:
        """Get current values for major market indices (S&P 500, Dow Jones, NASDAQ)."""
        try:
            indices = market_data_api.get_market_indices()
            if indices:
                result = "**Major Market Indices:**\n\n"
                for name, data in indices.items():
                    result += f"**{name}** ({data['symbol']})\n"
                    result += f"  Price: {data['price']:,.2f}\n"
                    result += f"  Change: {data['change']:,.2f} ({data['change_percent']:.2f}%)\n\n"
                return result
            return "Could not fetch market indices data."
        except Exception as e:
            return f"Error fetching market indices: {str(e)}"
    
    @tool
    def get_stock_news(symbol: str) -> str:
        """Get recent news articles about a specific stock."""
        try:
            articles = news_api.get_stock_news(symbol, limit=5)
            if articles:
                result = f"**Recent news for {symbol}:**\n\n"
                for idx, article in enumerate(articles, 1):
                    result += f"{idx}. **{article['title']}**\n"
                    result += f"   {article['description']}\n"
                    result += f"   Source: {article['source']} | {article['published_at']}\n\n"
                return result
            return f"No recent news found for {symbol}."
        except Exception as e:
            return f"Error fetching stock news: {str(e)}"
    
    market_analyst_tools = [get_stock_quote, get_company_information, get_market_indices, get_stock_news]
    
    # Define tools for Goal Planner Agent
    @tool
    def calculate_retirement_savings(current_age: int, retirement_age: int, monthly_contribution: float, expected_return: float, current_savings: float = 0) -> str:
        """Calculate projected retirement savings based on contributions and returns."""
        try:
            years = retirement_age - current_age
            if years <= 0:
                return "Retirement age must be greater than current age."
            
            months = years * 12
            monthly_rate = expected_return / 12 / 100
            
            # Future value of current savings
            fv_current = current_savings * ((1 + monthly_rate) ** months)
            
            # Future value of monthly contributions (annuity)
            if monthly_rate > 0:
                fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                fv_contributions = monthly_contribution * months
            
            total_fv = fv_current + fv_contributions
            total_contributions = (monthly_contribution * months) + current_savings
            
            result = f"**Retirement Savings Projection**\n\n"
            result += f"Current Age: {current_age} | Retirement Age: {retirement_age} | Years: {years}\n"
            result += f"Monthly Contribution: ${monthly_contribution:,.2f}\n"
            result += f"Expected Annual Return: {expected_return}%\n"
            result += f"Current Savings: ${current_savings:,.2f}\n\n"
            result += f"**Projected Results:**\n"
            result += f"Total Contributions: ${total_contributions:,.2f}\n"
            result += f"Investment Growth: ${total_fv - total_contributions:,.2f}\n"
            result += f"**Projected Balance at {retirement_age}: ${total_fv:,.2f}**\n\n"
            result += f"Note: This is an educational calculation. Actual results will vary based on market performance."
            
            return result
        except Exception as e:
            return f"Error calculating retirement savings: {str(e)}"
    
    @tool
    def calculate_savings_goal(goal_amount: float, timeframe_years: int, current_savings: float = 0, expected_return: float = 7.0) -> str:
        """Calculate required monthly savings to reach a financial goal."""
        try:
            if timeframe_years <= 0:
                return "Timeframe must be greater than 0 years."
            
            months = timeframe_years * 12
            monthly_rate = expected_return / 12 / 100
            
            # Calculate future value of current savings
            fv_current = current_savings * ((1 + monthly_rate) ** months)
            
            # Amount still needed
            amount_needed = goal_amount - fv_current
            
            if amount_needed <= 0:
                return f"Your current savings of ${current_savings:,.2f} will grow to ${fv_current:,.2f} in {timeframe_years} years, which exceeds your goal of ${goal_amount:,.2f}!"
            
            # Calculate required monthly payment
            if monthly_rate > 0:
                required_monthly = amount_needed / (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                required_monthly = amount_needed / months
            
            total_contributions = required_monthly * months
            
            result = f"**Savings Goal Calculation**\n\n"
            result += f"Goal Amount: ${goal_amount:,.2f}\n"
            result += f"Timeframe: {timeframe_years} years ({months} months)\n"
            result += f"Current Savings: ${current_savings:,.2f}\n"
            result += f"Expected Annual Return: {expected_return}%\n\n"
            result += f"**Required Monthly Savings: ${required_monthly:,.2f}**\n\n"
            result += f"Total Contributions: ${total_contributions:,.2f}\n"
            result += f"Investment Growth: ${goal_amount - total_contributions - current_savings:,.2f}\n\n"
            result += f"Tip: Even small increases in your monthly savings can significantly impact your goal!"
            
            return result
        except Exception as e:
            return f"Error calculating savings goal: {str(e)}"
    
    goal_planner_tools = [calculate_retirement_savings, calculate_savings_goal]
    
    # Define tools for Tax Educator Agent
    @tool
    def compare_retirement_accounts(account_types: str = "traditional_ira,roth_ira,401k") -> str:
        """Compare different retirement account types. Options: traditional_ira, roth_ira, 401k, 403b, hsa"""
        try:
            accounts_info = {
                'traditional_ira': {
                    'name': 'Traditional IRA',
                    'tax_treatment': 'Tax-deductible contributions, taxed at withdrawal',
                    'contribution_limit_2024': '$7,000 ($8,000 if 50+)',
                    'rmd': 'Required at age 73',
                    'best_for': 'Those expecting lower tax bracket in retirement'
                },
                'roth_ira': {
                    'name': 'Roth IRA',
                    'tax_treatment': 'After-tax contributions, tax-free withdrawals',
                    'contribution_limit_2024': '$7,000 ($8,000 if 50+)',
                    'rmd': 'No RMDs during owner\'s lifetime',
                    'best_for': 'Those expecting higher tax bracket in retirement'
                },
                '401k': {
                    'name': '401(k)',
                    'tax_treatment': 'Pre-tax contributions, taxed at withdrawal',
                    'contribution_limit_2024': '$23,000 ($30,500 if 50+)',
                    'rmd': 'Required at age 73',
                    'best_for': 'Maximizing tax-deferred savings with employer match'
                },
                '403b': {
                    'name': '403(b)',
                    'tax_treatment': 'Pre-tax contributions, taxed at withdrawal',
                    'contribution_limit_2024': '$23,000 ($30,500 if 50+)',
                    'rmd': 'Required at age 73',
                    'best_for': 'Non-profit and public sector employees'
                },
                'hsa': {
                    'name': 'Health Savings Account',
                    'tax_treatment': 'Triple tax advantage: deductible, grows tax-free, tax-free for medical',
                    'contribution_limit_2024': '$4,150 individual, $8,300 family (+$1,000 if 55+)',
                    'rmd': 'None',
                    'best_for': 'High-deductible health plan holders planning for medical expenses'
                }
            }
            
            requested_accounts = [a.strip().lower() for a in account_types.split(',')]
            
            result = "**Retirement Account Comparison:**\n\n"
            for account_type in requested_accounts:
                if account_type in accounts_info:
                    info = accounts_info[account_type]
                    result += f"**{info['name']}**\n"
                    result += f"  Tax Treatment: {info['tax_treatment']}\n"
                    result += f"  2024 Contribution Limit: {info['contribution_limit_2024']}\n"
                    result += f"  RMDs: {info['rmd']}\n"
                    result += f"  Best For: {info['best_for']}\n\n"
            
            result += "Note: Consult with a tax professional for your specific situation."
            return result
        except Exception as e:
            return f"Error comparing accounts: {str(e)}"
    
    @tool
    def explain_capital_gains_tax(holding_period: str = "both") -> str:
        """Explain capital gains tax. Options: short_term, long_term, both"""
        try:
            result = "**Capital Gains Tax Education:**\n\n"
            
            if holding_period in ["short_term", "both"]:
                result += "**Short-Term Capital Gains (held ≤ 1 year)**\n"
                result += "- Taxed as ordinary income at your marginal tax rate\n"
                result += "- Rates range from 10% to 37% (2024)\n"
                result += "- No preferential treatment\n\n"
            
            if holding_period in ["long_term", "both"]:
                result += "**Long-Term Capital Gains (held > 1 year)**\n"
                result += "- Preferential tax rates: 0%, 15%, or 20%\n"
                result += "- 0% rate: Income up to ~$44,625 (single) / ~$89,250 (married)\n"
                result += "- 15% rate: Income up to ~$492,300 (single) / ~$553,850 (married)\n"
                result += "- 20% rate: Income above those thresholds\n\n"
            
            result += "**Key Takeaways:**\n"
            result += "- Holding investments longer than 1 year can significantly reduce taxes\n"
            result += "- Tax rates depend on total taxable income\n"
            result += "- These are federal rates; state taxes may also apply\n\n"
            result += "Always consult a tax professional for your specific situation."
            
            return result
        except Exception as e:
            return f"Error explaining capital gains: {str(e)}"
    
    @tool
    def explain_tax_loss_harvesting() -> str:
        """Explain the concept and benefits of tax-loss harvesting."""
        try:
            result = "**Tax-Loss Harvesting Explained:**\n\n"
            result += "**What is it?**\n"
            result += "A strategy of selling investments at a loss to offset capital gains and reduce taxes.\n\n"
            result += "**How it works:**\n"
            result += "1. Sell investments that have decreased in value\n"
            result += "2. Realize the loss for tax purposes\n"
            result += "3. Use losses to offset capital gains\n"
            result += "4. Up to $3,000 of excess losses can offset ordinary income\n"
            result += "5. Remaining losses carry forward to future years\n\n"
            result += "**Important Rules:**\n"
            result += "- **Wash Sale Rule**: Can't buy the same/substantially identical security within 30 days before or after the sale\n"
            result += "- Applies to losses, not gains\n"
            result += "- Must be done in taxable accounts (not IRAs/401ks)\n\n"
            result += "**Benefits:**\n"
            result += "- Reduces current year tax liability\n"
            result += "- Maintains market exposure (by buying similar securities)\n"
            result += "- Can improve after-tax returns\n\n"
            result += "**Example:**\n"
            result += "You have $10,000 in capital gains and $4,000 in losses.\n"
            result += "Net capital gain: $6,000 (taxed instead of $10,000)\n\n"
            result += "Note: This is complex. Work with a tax professional to implement properly."
            
            return result
        except Exception as e:
            return f"Error explaining tax-loss harvesting: {str(e)}"
    
    tax_educator_tools = [compare_retirement_accounts, explain_capital_gains_tax, explain_tax_loss_harvesting]
    
    # Create agent instances
    agents = {
        "finance_qa": FinanceQAAgent(llm, finance_qa_tools),
        "portfolio_analyzer": PortfolioAnalyzerAgent(llm, portfolio_analyzer_tools),
        "market_analyst": MarketAnalystAgent(llm, market_analyst_tools),
        "goal_planner": GoalPlannerAgent(llm, goal_planner_tools),
        "tax_educator": TaxEducatorAgent(llm, tax_educator_tools)
    }
    
    logger.info(f"✅ Created {len(agents)} specialized finance agents")
    return agents
