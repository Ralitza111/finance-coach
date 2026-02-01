"""
Finance Coach Evaluation Runner
Run evaluations on Finance Coach using LangSmith
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_openai import ChatOpenAI

# Import Finance Coach components
from app import AIFinanceAssistant
from evaluation import (
    FinanceEvaluationDataset,
    create_evaluators
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment variables and LangSmith."""
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    # Setup LangSmith (optional but recommended)
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    if langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv(
            "LANGCHAIN_PROJECT",
            f"finance-coach-eval-{datetime.now().strftime('%Y%m%d')}"
        )
        logger.info(f"✅ LangSmith tracking enabled: {os.environ['LANGCHAIN_PROJECT']}")
    else:
        logger.warning("⚠️  LANGCHAIN_API_KEY not found - LangSmith tracking disabled")
    
    return openai_key, langchain_api_key


def create_finance_coach_evaluator(assistant: AIFinanceAssistant):
    """
    Create a function that wraps Finance Coach for evaluation.
    
    Args:
        assistant: AIFinanceAssistant instance
        
    Returns:
        Function that takes inputs dict and returns outputs dict
    """
    def evaluate_query(inputs: dict) -> dict:
        """
        Evaluate a single query through Finance Coach.
        
        Args:
            inputs: Dictionary with 'input' key containing the query
            
        Returns:
            Dictionary with 'output' key containing the response
        """
        query = inputs.get("input", "")
        
        try:
            # Process query through Finance Coach
            response, routing_info = assistant.process_query(query, thread_id="evaluation")
            
            return {
                "output": response,
                "routing_info": routing_info
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "output": f"Error: {str(e)}",
                "routing_info": "Error"
            }
    
    return evaluate_query


def run_evaluation(
    dataset_name: str = "finance-coach-eval",
    experiment_name: str = None,
    recreate_dataset: bool = False
):
    """
    Run comprehensive evaluation on Finance Coach.
    
    Args:
        dataset_name: Name of LangSmith dataset
        experiment_name: Name for this evaluation run
        recreate_dataset: Whether to recreate the dataset
    """
    logger.info("🚀 Starting Finance Coach Evaluation")
    logger.info("=" * 60)
    
    # Setup environment
    openai_key, langchain_key = setup_environment()
    
    # Initialize LangSmith client
    if langchain_key:
        client = Client()
        logger.info("✅ LangSmith client initialized")
    else:
        logger.warning("⚠️  Running without LangSmith - results won't be persisted")
        client = None
    
    # Create or load dataset
    if client:
        logger.info(f"📊 Setting up dataset: {dataset_name}")
        
        if recreate_dataset:
            try:
                # Delete existing dataset
                existing = client.read_dataset(dataset_name=dataset_name)
                client.delete_dataset(dataset_id=existing.id)
                logger.info(f"🗑️  Deleted existing dataset")
            except Exception:
                pass
        
        # Create dataset
        dataset = FinanceEvaluationDataset.create_langsmith_dataset(
            client,
            dataset_name=dataset_name
        )
        logger.info(f"✅ Dataset ready: {len(FinanceEvaluationDataset.TEST_CASES)} test cases")
    else:
        logger.info("📊 Using local dataset (LangSmith not available)")
        dataset = dataset_name  # Will use local data
    
    # Initialize Finance Coach
    logger.info("🤖 Initializing Finance Coach...")
    assistant = AIFinanceAssistant(
        openai_api_key=openai_key,
        alpha_vantage_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
        news_api_key=os.getenv("NEWS_API_KEY")
    )
    logger.info("✅ Finance Coach initialized")
    
    # Create evaluator function
    evaluator_func = create_finance_coach_evaluator(assistant)
    
    # Get evaluators
    evaluators = create_evaluators()
    logger.info(f"📋 Loaded {len(evaluators)} evaluators:")
    evaluator_names = [
        "1. Disclaimer Presence",
        "2. Safety & Compliance",
        "3. Financial Accuracy",
        "4. Response Quality",
        "5. Educational Tone",
        "6. LLM-as-Judge (GPT-4o-mini)"
    ]
    for name in evaluator_names:
        logger.info(f"   {name}")
    
    # Run evaluation
    if not experiment_name:
        experiment_name = f"finance-coach-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    logger.info(f"\n⚡ Running evaluation: {experiment_name}")
    logger.info("=" * 60)
    
    try:
        if client:
            # Run with LangSmith
            results = evaluate(
                evaluator_func,
                data=dataset_name,
                evaluators=evaluators,
                experiment_prefix=experiment_name,
                num_repetitions=1  # Run each example once
            )
            
            logger.info("\n✅ Evaluation complete!")
            logger.info("=" * 60)
            logger.info(f"📊 Results saved to LangSmith")
            logger.info(f"🔗 View at: https://smith.langchain.com")
            logger.info(f"📁 Project: {os.environ.get('LANGCHAIN_PROJECT')}")
            logger.info(f"📝 Experiment: {experiment_name}")
            
        else:
            # Run locally without LangSmith
            logger.info("Running evaluation locally...")
            test_cases = FinanceEvaluationDataset.get_dataset()
            
            results = []
            for i, case in enumerate(test_cases, 1):
                logger.info(f"\nTest {i}/{len(test_cases)}: {case['category']}")
                logger.info(f"Q: {case['input'][:80]}...")
                
                # Run through Finance Coach
                output = evaluator_func({"input": case["input"]})
                response = output["output"]
                
                logger.info(f"A: {response[:100]}...")
                
                # Mock run object for evaluators
                class MockRun:
                    def __init__(self, outputs):
                        self.outputs = outputs
                
                # Mock example object
                class MockExample:
                    def __init__(self, inputs, outputs):
                        self.inputs = inputs
                        self.outputs = outputs
                
                run = MockRun({"output": response})
                example = MockExample(
                    {"input": case["input"]},
                    {"output": case["output"]}
                )
                
                # Run evaluators
                eval_results = {}
                for evaluator in evaluators:
                    result = evaluator(run, example)
                    eval_results[evaluator.__name__] = result
                
                results.append({
                    "case": case,
                    "response": response,
                    "evaluations": eval_results
                })
                
                # Print evaluation summary
                avg_score = sum(r["score"] for r in eval_results.values()) / len(eval_results)
                logger.info(f"Average Score: {avg_score:.2f}")
            
            logger.info("\n✅ Local evaluation complete!")
            logger.info(f"📊 Evaluated {len(results)} test cases")
            
            # Print summary
            print_evaluation_summary(results)
    
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}", exc_info=True)
        raise
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Evaluation complete!")


def print_evaluation_summary(results: list):
    """Print summary of evaluation results."""
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    
    # Calculate average scores per evaluator
    evaluator_scores = {}
    for result in results:
        for eval_name, eval_result in result["evaluations"].items():
            if eval_name not in evaluator_scores:
                evaluator_scores[eval_name] = []
            evaluator_scores[eval_name].append(eval_result["score"])
    
    print("\n📋 Average Scores by Evaluator:")
    for eval_name, scores in evaluator_scores.items():
        avg_score = sum(scores) / len(scores)
        print(f"  {eval_name}: {avg_score:.3f}")
    
    # Overall average
    all_scores = [score for scores in evaluator_scores.values() for score in scores]
    overall_avg = sum(all_scores) / len(all_scores)
    print(f"\n🎯 Overall Average: {overall_avg:.3f}")
    
    # Category breakdown
    category_scores = {}
    for result in results:
        category = result["case"]["category"]
        if category not in category_scores:
            category_scores[category] = []
        
        avg_score = sum(e["score"] for e in result["evaluations"].values()) / len(result["evaluations"])
        category_scores[category].append(avg_score)
    
    print("\n📂 Scores by Category:")
    for category, scores in sorted(category_scores.items()):
        avg_score = sum(scores) / len(scores)
        print(f"  {category}: {avg_score:.3f} ({len(scores)} tests)")
    
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Finance Coach evaluation")
    parser.add_argument(
        "--dataset",
        default="finance-coach-eval",
        help="Dataset name in LangSmith"
    )
    parser.add_argument(
        "--experiment",
        help="Experiment name (auto-generated if not provided)"
    )
    parser.add_argument(
        "--recreate-dataset",
        action="store_true",
        help="Recreate the dataset from scratch"
    )
    
    args = parser.parse_args()
    
    run_evaluation(
        dataset_name=args.dataset,
        experiment_name=args.experiment,
        recreate_dataset=args.recreate_dataset
    )
