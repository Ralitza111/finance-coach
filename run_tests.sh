#!/bin/bash

# Test Runner Script for AI Finance Assistant
# This script provides convenient commands to run different test suites

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 AI Finance Assistant - Test Runner${NC}"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated. Activating...${NC}"
    source venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest pytest-cov
fi

# Function to run tests with coverage
run_with_coverage() {
    echo -e "${GREEN}Running tests with coverage...${NC}"
    pytest --cov=. --cov-report=term-missing --cov-report=html "$@"
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
}

# Function to run specific test suite
run_suite() {
    case $1 in
        all)
            echo -e "${GREEN}Running all tests...${NC}"
            pytest -v "$@"
            ;;
        routing)
            echo -e "${GREEN}Running routing tests...${NC}"
            pytest tests/test_multi_agent.py::TestRouting -v
            ;;
        agents)
            echo -e "${GREEN}Running agent tests...${NC}"
            pytest tests/test_multi_agent.py::TestAgents -v
            ;;
        orchestrator)
            echo -e "${GREEN}Running orchestrator tests...${NC}"
            pytest tests/test_multi_agent.py::TestOrchestrator -v
            ;;
        api)
            echo -e "${GREEN}Running API client tests...${NC}"
            pytest tests/test_market_data_api.py -v
            ;;
        tools)
            echo -e "${GREEN}Running tool tests...${NC}"
            pytest tests/test_tools.py -v
            ;;
        integration)
            echo -e "${GREEN}Running integration tests...${NC}"
            pytest -m integration -v
            ;;
        quick)
            echo -e "${GREEN}Running quick tests (no API calls)...${NC}"
            pytest -m "not api and not slow" -v
            ;;
        *)
            echo -e "${RED}Unknown test suite: $1${NC}"
            echo "Available suites: all, routing, agents, orchestrator, api, tools, integration, quick"
            exit 1
            ;;
    esac
}

# Parse command line arguments
case ${1:-all} in
    coverage)
        shift
        run_with_coverage "$@"
        ;;
    help|--help|-h)
        echo "Usage: ./run_tests.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  all          - Run all tests (default)"
        echo "  routing      - Run routing tests only"
        echo "  agents       - Run agent tests only"
        echo "  orchestrator - Run orchestrator tests only"
        echo "  api          - Run API client tests only"
        echo "  tools        - Run tool tests only"
        echo "  integration  - Run integration tests only"
        echo "  quick        - Run quick tests (skip API/slow tests)"
        echo "  coverage     - Run all tests with coverage report"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests"
        echo "  ./run_tests.sh routing            # Run routing tests"
        echo "  ./run_tests.sh coverage           # Run with coverage"
        echo "  ./run_tests.sh quick              # Run quick tests"
        ;;
    *)
        run_suite "$@"
        ;;
esac

echo ""
echo -e "${GREEN}✅ Test run complete!${NC}"
