"""
Pytest configuration and fixtures for AI Finance Assistant tests
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def api_keys():
    """Fixture to provide API keys for tests"""
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
        "news_api": os.getenv("NEWS_API_KEY")
    }


@pytest.fixture(scope="session")
def llm_model():
    """Fixture to provide LLM model name"""
    return os.getenv("LLM_MODEL", "gpt-4o-mini")


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API calls"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark API tests
        if "api" in item.nodeid.lower() or "test_market_data_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
