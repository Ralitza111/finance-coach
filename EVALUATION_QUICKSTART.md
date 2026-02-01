# 🚀 Quick Start: Running Evaluations

## Prerequisites

1. **OpenAI API Key** (Required)
   - Get from: https://platform.openai.com/api-keys

2. **LangSmith API Key** (Optional but recommended)
   - Get from: https://smith.langchain.com
   - Free tier available
   - Enables dashboard tracking and historical analysis

## Setup (One-Time)

### Step 1: Check your .env file

```bash
cd ~/Documents/finance-coach
cat .env
```

Make sure it has:
```bash
OPENAI_API_KEY=sk-...your-key...
LANGCHAIN_API_KEY=ls_...your-key...  # Optional
```

If you don't have a `.env` file, create one:
```bash
echo "OPENAI_API_KEY=your-openai-key-here" > .env
echo "LANGCHAIN_API_KEY=your-langsmith-key-here" >> .env  # Optional
```

### Step 2: Install dependencies (if not already done)

```bash
pip install langsmith langchain_openai
# or
pip install -r requirements.txt
```

## Running Evaluations

### Method 1: Use the Quick Script (Easiest!) 🎯

```bash
cd ~/Documents/finance-coach
./quick_eval.sh
```

**With options:**
```bash
# Recreate dataset
./quick_eval.sh --recreate-dataset

# Custom experiment name
./quick_eval.sh --experiment "my-test-run"

# Help
./quick_eval.sh --help
```

### Method 2: Direct Python Command

```bash
cd ~/Documents/finance-coach

# Load environment and run
export $(cat .env | grep -v '^#' | xargs)
python3 run_evaluation.py
```

**With options:**
```bash
# Recreate dataset
python3 run_evaluation.py --recreate-dataset

# Custom experiment name
python3 run_evaluation.py --experiment "my-test-run"

# Custom dataset name
python3 run_evaluation.py --dataset "my-dataset"
```

### Method 3: From Python Code

```python
from run_evaluation import run_evaluation

# Run with defaults
run_evaluation()

# With custom options
run_evaluation(
    dataset_name="finance-coach-eval",
    experiment_name="pre-deploy-test",
    recreate_dataset=False
)
```

## What Happens During Evaluation?

1. ✅ **Loads Environment** - Checks for API keys
2. ✅ **Initializes Finance Coach** - Starts up all agents
3. ✅ **Loads Dataset** - 14 test cases covering all agents
4. ✅ **Runs Tests** - Each case through all 6 evaluators
5. ✅ **Generates Scores** - Calculates metrics
6. ✅ **Shows Results** - Prints summary to console
7. ✅ **Uploads to LangSmith** - If LANGCHAIN_API_KEY is set

**Expected runtime:** 2-5 minutes (depends on API response times)

## Understanding Results

### Console Output

You'll see something like:

```
📊 EVALUATION SUMMARY
============================================================

📋 Average Scores by Evaluator:
  disclaimer_presence_evaluator: 0.933
  safety_compliance_evaluator: 1.000  ✅
  financial_accuracy_evaluator: 0.756
  response_quality_evaluator: 0.867
  educational_tone_evaluator: 0.912
  llm_judge_evaluator: 0.845

🎯 Overall Average: 0.885  ✅ EXCELLENT!

📂 Scores by Category:
  compliance_test: 0.950 (3 tests)
  finance_qa: 0.878 (3 tests)
  goal_planner: 0.867 (2 tests)
```

### Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 0.9 - 1.0 | Excellent ✅ | Keep it up! |
| 0.8 - 0.9 | Good ✅ | Minor tweaks |
| 0.7 - 0.8 | Acceptable 🟡 | Review failures |
| 0.6 - 0.7 | Needs work 🟡 | Investigate |
| < 0.6 | Poor ❌ | Fix required |

### Red Flags 🚩

**These should always be 1.0:**
- `disclaimer_presence_evaluator` - Legal requirement!
- `safety_compliance_evaluator` - User safety!

If either is below 1.0, review the failing cases immediately.

## Viewing Results in LangSmith

If you set `LANGCHAIN_API_KEY`:

1. Go to: https://smith.langchain.com
2. Navigate to your project (default: `finance-coach-eval`)
3. View detailed results:
   - Individual test runs
   - Score breakdowns
   - Comparison charts
   - Historical trends

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"

**Solution:**
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Or export directly
export OPENAI_API_KEY="sk-your-key"
```

### Issue: "ModuleNotFoundError: No module named 'langsmith'"

**Solution:**
```bash
pip install langsmith
# or
pip install -r requirements.txt
```

### Issue: Evaluation runs but scores are low

**What to check:**
1. Review logs: `logs/finance_assistant_*.log`
2. Check which specific tests failed
3. Run app manually to see if agents work: `python3 app.py`
4. Review recent code changes

### Issue: "Error processing query"

**Common causes:**
- API rate limits hit
- Network issues
- Agent initialization failure

**Solution:**
1. Check `logs/` folder for detailed errors
2. Verify API keys are valid
3. Try running with fewer test cases
4. Check your internet connection

### Issue: Takes too long

**Solutions:**
- Remove LLM Judge evaluator (slowest one)
- Reduce number of test cases
- Use gpt-3.5-turbo instead of gpt-4

## Advanced Usage

### Run Specific Categories Only

Edit `run_evaluation.py` and modify the dataset loading:

```python
# Only run tax education tests
from evaluation import FinanceEvaluationDataset
tax_cases = FinanceEvaluationDataset.get_by_category("tax_educator")
```

### Add Your Own Test Cases

Edit `evaluation.py` and add to `TEST_CASES`:

```python
{
    "input": "Your test question",
    "output": "Expected answer",
    "category": "finance_qa",
    "tags": ["your", "tags"]
}
```

### Custom Evaluators

Create your own in `evaluation.py`:

```python
@staticmethod
def my_custom_evaluator(run, example):
    answer = FinanceEvaluators.get_answer_text(run)
    # Your logic here
    return {"score": 0.0-1.0, "comment": "Your comment"}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Evaluations
on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
        run: python3 run_evaluation.py
```

## Next Steps

1. **Run your first evaluation:**
   ```bash
   ./quick_eval.sh
   ```

2. **Review the results** in console or LangSmith

3. **Set up regular evaluations:**
   - Before each deployment
   - After significant changes
   - Weekly automated runs

4. **Read full documentation:**
   - `EVALUATION.md` - Complete guide
   - `evaluation.py` - Code with comments
   - `EVALUATION_IMPLEMENTATION.md` - Technical details

## Questions?

- Check `EVALUATION.md` for detailed documentation
- Review `evaluation.py` code for examples
- Open an issue if something doesn't work

---

**Happy Evaluating! 📊✨**
