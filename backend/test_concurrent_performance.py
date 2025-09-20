#!/usr/bin/env python3
"""
Test script to demonstrate the performance improvement of concurrent agent execution
"""
import os
import time
import logging
from agents.financial_workflow import FinancialWorkflow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_concurrent_performance():
    """Test the concurrent execution performance"""
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    # Initialize the workflow
    logger.info("Initializing FinancialWorkflow with concurrent execution")
    workflow = FinancialWorkflow(openai_api_key)
    
    # Test with sample data
    sample_file = "data/Synthetic_Bakery_GeneralLedger.csv"
    
    if not os.path.exists(sample_file):
        logger.error(f"Sample file not found: {sample_file}")
        return
    
    # Measure execution time
    start_time = time.time()
    
    try:
        logger.info("Starting workflow execution...")
        result = workflow.process_file(sample_file)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"Workflow completed successfully!")
        logger.info(f"Total execution time: {execution_time:.2f} seconds")
        
        # Print some basic stats about the result
        if result and not result.get("error"):
            tiles = result.get("tiles", {})
            logger.info(f"Generated tiles for {len(tiles)} metrics")
            
            insights = result.get("insights", {})
            if insights.get("overall_insights"):
                logger.info(f"Generated {len(insights['overall_insights'])} overall insights")
            
            narratives = result.get("narratives", {})
            logger.info(f"Generated narratives for {len(narratives)} metrics")
            
        else:
            logger.error(f"Workflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"Workflow failed after {execution_time:.2f} seconds: {str(e)}")

if __name__ == "__main__":
    test_concurrent_performance()
