#!/bin/bash
# Quick Evaluation Runner for Finance Coach
# This script makes it easy to run evaluations

echo "🚀 Finance Coach Evaluation Runner"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "run_evaluation.py" ]; then
    echo "❌ Error: Please run this script from the finance-coach directory"
    echo "   cd ~/Documents/finance-coach && ./quick_eval.sh"
    exit 1
fi

# Check for .env file
if [ -f ".env" ]; then
    echo "✅ Found .env file, loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found"
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "❌ OPENAI_API_KEY not set!"
    echo ""
    echo "Please set it in one of these ways:"
    echo "  1. Create a .env file with: OPENAI_API_KEY=your-key"
    echo "  2. Export it: export OPENAI_API_KEY='your-key'"
    echo ""
    exit 1
fi

# Check for LangSmith
if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "⚠️  LANGCHAIN_API_KEY not set - running locally without LangSmith"
    echo "   (Results won't be uploaded to LangSmith dashboard)"
    echo ""
    echo "   To enable LangSmith tracking:"
    echo "   1. Get API key from: https://smith.langchain.com"
    echo "   2. Add to .env: LANGCHAIN_API_KEY=your-langsmith-key"
    echo ""
else
    echo "✅ LangSmith enabled - results will be uploaded"
    export LANGCHAIN_TRACING_V2="true"
    export LANGCHAIN_PROJECT="${LANGCHAIN_PROJECT:-finance-coach-eval}"
    echo "   Project: $LANGCHAIN_PROJECT"
    echo ""
fi

# Parse command line arguments
RECREATE_DATASET=false
EXPERIMENT_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --recreate-dataset)
            RECREATE_DATASET=true
            shift
            ;;
        --experiment)
            EXPERIMENT_NAME="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./quick_eval.sh [options]"
            echo ""
            echo "Options:"
            echo "  --recreate-dataset    Recreate the evaluation dataset"
            echo "  --experiment NAME     Custom experiment name"
            echo "  --help, -h           Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 run_evaluation.py"
if [ "$RECREATE_DATASET" = true ]; then
    CMD="$CMD --recreate-dataset"
fi
if [ -n "$EXPERIMENT_NAME" ]; then
    CMD="$CMD --experiment '$EXPERIMENT_NAME'"
fi

echo "📊 Running evaluation..."
echo "Command: $CMD"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Run the evaluation
eval $CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ Evaluation completed successfully!"
    echo ""
    if [ -n "$LANGCHAIN_API_KEY" ]; then
        echo "🔗 View results at: https://smith.langchain.com"
        echo "📁 Project: $LANGCHAIN_PROJECT"
    else
        echo "💡 Tip: Set LANGCHAIN_API_KEY to enable dashboard tracking"
    fi
else
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "❌ Evaluation failed!"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check that all dependencies are installed: pip install -r requirements.txt"
    echo "  2. Verify your API keys are correct"
    echo "  3. Check logs/finance_assistant_*.log for details"
fi
