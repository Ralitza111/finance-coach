# AI Finance Assistant - Test Suite

Comprehensive test suite for the AI Finance Assistant multi-agent system.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_multi_agent.py      # Main multi-agent system tests
├── test_market_data_api.py  # Market data API client tests
└── test_tools.py            # Individual tool function tests
```

## Test Categories

### 1. Routing Tests (`test_multi_agent.py::TestRouting`)
Tests that queries are routed to the correct specialized agent:
- Finance Q&A routing
- Portfolio Analyzer routing
- Market Analyst routing
- Goal Planner routing
- Tax Educator routing
- Complex multi-agent queries

### 2. Agent Tests (`test_multi_agent.py::TestAgents`)
Tests agent creation and functionality:
- Agent initialization
- Tool availability
- Agent configuration

### 3. Orchestrator Tests (`test_multi_agent.py::TestOrchestrator`)
Tests the multi-agent orchestrator:
- Query processing
- Agent coordination
- Response generation

### 4. API Client Tests (`test_market_data_api.py`)
Tests the market data API client:
- Stock quote fetching
- Company information retrieval
- Market indices data
- Caching functionality
- Rate limiting
- Error handling

### 5. Tool Tests (`test_tools.py`)
Tests individual tool functions:
- Finance Q&A tools (search terms, educational content)
- Portfolio analysis tools (allocation, diversification)
- Market analyst tools (quotes, news, indices)
- Goal planning tools (retirement, savings calculations)
- Tax education tools (account comparisons, tax strategies)

### 6. Integration Tests (`test_multi_agent.py::TestIntegration`)
End-to-end tests of complete workflows:
- Simple queries
- Complex multi-step queries
- Real-world scenarios

## Running Tests

### Run All Tests
```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=html
```

### Run Specific Test Files
```bash
# Run only multi-agent tests
pytest tests/test_multi_agent.py

# Run only API tests
pytest tests/test_market_data_api.py

# Run only tool tests
pytest tests/test_tools.py
```

### Run Specific Test Classes
```bash
# Run routing tests
pytest tests/test_multi_agent.py::TestRouting

# Run agent tests
pytest tests/test_multi_agent.py::TestAgents

# Run API tests
pytest tests/test_market_data_api.py::TestMarketDataAPI
```

### Run Specific Test Methods
```bash
# Run a specific test
pytest tests/test_multi_agent.py::TestRouting::test_finance_qa_routing

# Run tests matching a pattern
pytest -k "routing"
pytest -k "portfolio"
```

### Run Tests by Marker
```bash
# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

## Test Markers

- `@pytest.mark.integration` - Integration tests (may be slow)
- `@pytest.mark.api` - Tests that make actual API calls
- `@pytest.mark.slow` - Long-running tests

## Prerequisites

1. **Environment Variables**: Ensure `.env` file is configured with:
   ```
   OPENAI_API_KEY=your_key_here
   ALPHA_VANTAGE_API_KEY=your_key_here
   NEWS_API_KEY=your_key_here
   LLM_MODEL=gpt-4o-mini
   ```

2. **Dependencies**: Install test dependencies:
   ```bash
   pip install pytest pytest-cov python-dotenv
   ```

3. **Virtual Environment**: Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   ```

## Test Coverage

Generate test coverage report:
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
```

## Debugging Tests

### Run with detailed output
```bash
pytest -vv --tb=long
```

### Run with print statements
```bash
pytest -s
```

### Run with pdb on failure
```bash
pytest --pdb
```

### Run last failed tests
```bash
pytest --lf
```

## Writing New Tests

### Test Naming Convention
- File: `test_*.py`
- Class: `Test*`
- Method: `test_*`

### Example Test
```python
def test_my_feature(orchestrator):
    """Test description"""
    # Arrange
    query = "test query"
    
    # Act
    result = orchestrator.process_query(query)
    
    # Assert
    assert isinstance(result, dict)
    assert "response" in result
```

### Using Fixtures
```python
def test_with_agents(agents):
    """Test using the agents fixture"""
    assert len(agents) == 5
    assert "finance_qa" in agents
```

## Known Issues

1. **API Rate Limiting**: Yahoo Finance API may return 429 errors. Tests include fallback handling.
2. **Network Dependencies**: Some tests require internet connection for API calls.
3. **API Keys**: Tests will skip if API keys are not configured (use `pytest.skip`).

## Test Results

Expected test results:
- ✅ All routing tests should pass
- ✅ Agent creation tests should pass
- ⚠️  Market data tests may show warnings due to rate limiting
- ✅ Tool tests should pass with proper error handling
- ✅ Integration tests should complete successfully

## Support

For issues with tests:
1. Check `.env` file is properly configured
2. Verify all dependencies are installed
3. Check API keys are valid
4. Review test output for specific error messages

## Contributing

When adding new features:
1. Add corresponding tests
2. Ensure all tests pass
3. Maintain test coverage above 80%
4. Follow existing test patterns
