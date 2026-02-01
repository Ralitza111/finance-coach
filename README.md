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
- **🛡️ Comprehensive Guardrails System** for safety, compliance, and responsible AI interactions
- **📊 LangSmith Evaluation Framework** with 6 custom evaluators and 15 test cases

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
finance-coach/
├── app.py                      # Main Gradio application
├── market_data_api.py          # Market data integration (yFinance/Alpha Vantage)
├── news_api.py                 # Financial news API wrapper
├── web_scraper.py             # Educational content scraper
├── specialized_agents.py       # 5 specialized agent implementations
├── multi_agent_router.py       # Intelligent query routing
├── multi_agent_orchestrator.py # Agent coordination
├── guardrails.py              # Safety and compliance guardrails 🛡️
├── evaluation.py              # Evaluation system with custom evaluators 📊
├── run_evaluation.py          # Evaluation runner script
├── knowledge_base/            # FAISS vector store for RAG
│   └── faiss_index/
├── logs/                      # Application logs
├── tests/                     # Test suite
│   ├── test_agents.py
│   ├── test_apis.py
│   ├── test_guardrails.py    # Guardrails tests
│   └── test_integration.py
├── requirements.txt           # Python dependencies
├── GUARDRAILS.md             # Guardrails documentation 📋
├── EVALUATION.md             # Evaluation framework documentation 📊
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

## 🧪 Testing & Evaluation

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Test guardrails specifically
pytest tests/test_guardrails.py -v
```

### LangSmith Evaluation

The Finance Coach includes a comprehensive evaluation framework using LangSmith with **6 custom evaluators** and **15 test cases**. See [EVALUATION.md](EVALUATION.md) for complete documentation.

#### Quick Evaluation Run

```bash
# Set up environment
export OPENAI_API_KEY="your-key"
export LANGCHAIN_API_KEY="your-langsmith-key"  # Optional
export LANGCHAIN_TRACING_V2="true"

# Run evaluation
python3 run_evaluation.py
```

#### Evaluators

1. **Disclaimer Presence** 🛡️ - Ensures all responses include appropriate disclaimers
2. **Safety & Compliance** ⚖️ - Detects prohibited language and risky advice
3. **Financial Accuracy** ✅ - Measures factual correctness
4. **Response Quality** 📝 - Evaluates professionalism and completeness
5. **Educational Tone** 📚 - Ensures educational focus vs. specific advice
6. **LLM-as-Judge** 🤖 - GPT-4o-mini comprehensive evaluation

#### Evaluation Results

Example scores:
- Disclaimer Presence: **0.93** (Target: 1.0)
- Safety & Compliance: **1.00** ✅
- Financial Accuracy: **0.76**
- Response Quality: **0.87**
- Educational Tone: **0.91**
- LLM Judge: **0.85**
- **Overall Average: 0.89** 🎯

View detailed results in [LangSmith Dashboard](https://smith.langchain.com).

For detailed information about evaluation metrics, see [EVALUATION.md](EVALUATION.md).

## 🛡️ Guardrails & Safety

This application includes a comprehensive guardrails system to ensure safe, compliant, and responsible AI interactions. See [GUARDRAILS.md](GUARDRAILS.md) for complete documentation.

### Key Safety Features

1. **Input Validation**
   - Length limits and sanitization
   - Malicious pattern detection (SQL injection, XSS)
   - Prohibited content filtering

2. **Content Safety**
   - Blocks queries about illegal activities (pump & dump, insider trading, etc.)
   - Flags sensitive topics requiring extra disclaimers
   - Prevents promotion of risky/unethical practices

3. **Rate Limiting**
   - 10 queries per minute per session
   - 100 queries per hour per session
   - Prevents abuse and DoS attacks

4. **Output Validation**
   - Sanitizes overly prescriptive language
   - Automatically adds appropriate disclaimers
   - Ensures educational tone over financial advice

5. **Compliance**
   - Educational focus enforcement
   - Licensed professional referrals
   - Automatic risk warnings

### Example: Guardrail in Action

```python
# Prohibited query is blocked
User: "How can I manipulate stock prices?"
System: ⚠️ I cannot assist with questions about market manipulation...

# Rate limit protection
User: [11th query in 1 minute]
System: ⚠️ Too many requests. Please wait a moment...

# Output sanitization
Agent: "You must absolutely invest in this!"
System: "You might consider investing in this..." [with disclaimers]
```

For detailed information, configuration options, and troubleshooting, see [GUARDRAILS.md](GUARDRAILS.md).

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
