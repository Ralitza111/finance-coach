# 🏦 AI Finance Assistant - Multi-Agent System

An intelligent multi-agent conversational AI system that democratizes financial literacy through personalized education, real-time market data, and comprehensive financial planning tools.

## 🌟 Features

- **5 Specialized AI Agents** working together to provide comprehensive financial guidance
- **Real-time Market Data** from yFinance and Alpha Vantage APIs
- **RAG-Enhanced Responses** using FAISS vector database
- **Portfolio Analysis** with diversification insights
- **Financial Planning** calculators and goal setting
- **Tax Education** on retirement accounts and strategies
- **Market News Integration** with financial news sources

## 🤖 Agent Architecture

### 1. **Finance Q&A Agent** 💬
- Explains financial terms and concepts
- Answers general investment questions
- Provides educational resources
- Searches Investopedia definitions

### 2. **Portfolio Analyzer Agent** 📊
- Analyzes portfolio composition
- Assesses asset allocation and diversification
- Identifies concentration risks
- Calculates performance metrics

### 3. **Market Analyst Agent** 📈
- Fetches real-time stock quotes
- Provides company information
- Tracks major market indices
- Delivers relevant stock news

### 4. **Goal Planner Agent** 🎯
- Retirement savings calculations
- Financial goal planning
- Required savings calculator
- Risk tolerance assessment

### 5. **Tax Educator Agent** 💰
- Explains retirement account types (IRA, 401k, etc.)
- Capital gains tax education
- Tax-loss harvesting concepts
- RMD and account comparison tools

## 📁 Project Structure

```
finance-multi-agent/
├── market_data_api.py          # Market data integration (yFinance/Alpha Vantage)
├── news_api.py                 # Financial news API wrapper
├── web_scraper.py             # Educational content scraper
├── specialized_agents.py       # 5 specialized agent implementations
├── multi_agent_router.py       # Intelligent query routing
├── multi_agent_orchestrator.py # Agent coordination
├── multi_agent_finance.py      # Main application entry point
├── knowledge_base/            # FAISS vector store for RAG
│   └── faiss_index/
├── logs/                      # Application logs
├── tests/                     # Test suite
│   ├── test_agents.py
│   ├── test_apis.py
│   └── test_integration.py
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
cd finance-multi-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required: OPENAI_API_KEY
# Optional: ALPHA_VANTAGE_API_KEY, NEWS_API_KEY
```

### 3. Run the Application

```bash
# Basic CLI mode
python multi_agent_finance.py

# With Streamlit UI (recommended)
python multi_agent_finance.py --ui

# Specify user configuration
python multi_agent_finance.py --ui --user-age 30 --risk-tolerance moderate
```

## 🔑 API Keys Required

### Required:
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com/api-keys)

### Optional (Enhanced Features):
- **Alpha Vantage API Key**: Free tier at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
  - 5 API calls per minute, 500 per day
  - Used for additional market data
  
- **News API Key**: Free tier at [newsapi.org](https://newsapi.org/register)
  - 100 requests per day
  - Used for financial news integration

> **Note**: The system works with just OpenAI API key using yFinance (free, no key required) for market data.

## 💡 Usage Examples

### Example 1: Ask About Financial Terms
```
You: What is a diversified portfolio?

Finance Q&A Agent: A diversified portfolio is an investment strategy...
[Retrieves definition from knowledge base and Investopedia]
```

### Example 2: Analyze Your Portfolio
```
You: Analyze my portfolio: AAPL (10 shares), MSFT (15 shares), GOOGL (5 shares)

Portfolio Analyzer Agent: 
**Portfolio Analysis**
Total Value: $8,450.00

Holdings:
- AAPL: 10 shares @ $185.50 = $1,855.00 (21.9%)
- MSFT: 15 shares @ $378.20 = $5,673.00 (67.1%)
...
```

### Example 3: Check Stock Price
```
You: What's the current price of Tesla stock?

Market Analyst Agent:
**Tesla Inc (TSLA)**
Price: $248.50
Change: +$5.20 (+2.13%)
...
```

### Example 4: Plan for Retirement
```
You: I'm 30 and want to retire at 65. If I save $500/month with 7% return, how much will I have?

Goal Planner Agent:
**Retirement Savings Projection**
...
Projected Balance at 65: $749,176.43
```

### Example 5: Learn About Taxes
```
You: What's the difference between Traditional and Roth IRA?

Tax Educator Agent:
**Traditional IRA**
Tax Treatment: Tax-deductible contributions, taxed at withdrawal
...
**Roth IRA**
Tax Treatment: After-tax contributions, tax-free withdrawals
...
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## 📊 Data Sources

### Market Data
- **yFinance**: Real-time and historical stock data (primary, free)
- **Alpha Vantage**: Additional market data and indicators (optional)

### Financial News
- **NewsAPI**: Aggregated financial news from major sources
- **Sample Data**: Fallback when API unavailable

### Educational Content
- **Investopedia**: Financial term definitions and explanations
- **Built-in Knowledge Base**: Curated financial education content
- **Web Scraping**: Educational articles from trusted sources

See [DATA_SOURCES.md](DATA_SOURCES.md) for detailed information about each source.

## ⚠️ Important Disclaimers

- **NOT FINANCIAL ADVICE**: This system provides educational information only, not personalized financial advice
- **Consult Professionals**: Always consult licensed financial advisors and tax professionals for specific situations
- **Data Accuracy**: Market data may be delayed; verify critical information
- **Risk Warning**: All investments carry risk; past performance doesn't guarantee future results

## 🛠️ Technology Stack

- **LLM Framework**: LangChain + LangGraph
- **Language Model**: OpenAI GPT-4o-mini (configurable)
- **Vector Database**: FAISS (ChromaDB/Pinecone also supported)
- **Market Data**: yFinance + Alpha Vantage APIs
- **Web Interface**: Streamlit (Gradio alternative available)
- **Testing**: pytest with coverage

## 📈 Future Enhancements

- [ ] Voice interface integration
- [ ] Mobile app (React Native)
- [ ] Advanced portfolio analytics (Monte Carlo simulations)
- [ ] Cryptocurrency support
- [ ] International markets
- [ ] MCP server for Claude Desktop
- [ ] Real brokerage API integration
- [ ] Multi-language support

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for democratizing financial literacy**
