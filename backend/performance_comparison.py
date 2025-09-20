#!/usr/bin/env python3
"""
Performance comparison between sequential and concurrent agent execution
"""
import os
import time
import logging
import concurrent.futures
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_sequential_openai_calls():
    """Simulate sequential OpenAI API calls (old approach)"""
    logger.info("Simulating sequential OpenAI API calls...")
    
    start_time = time.time()
    
    # Simulate 4 sequential calls (like in the old data storyteller)
    for i in range(4):
        logger.info(f"Making sequential API call {i+1}/4")
        time.sleep(1)  # Simulate API call latency
    
    # Simulate 4 more sequential calls (like in the old advisor agent)
    for i in range(4):
        logger.info(f"Making sequential API call {i+5}/8")
        time.sleep(1)  # Simulate API call latency
    
    # Simulate 1 more call (overall business narrative)
    logger.info("Making final sequential API call 9/9")
    time.sleep(1)
    
    end_time = time.time()
    sequential_time = end_time - start_time
    
    logger.info(f"Sequential execution completed in {sequential_time:.2f} seconds")
    return sequential_time

def simulate_concurrent_openai_calls():
    """Simulate concurrent OpenAI API calls (new approach)"""
    logger.info("Simulating concurrent OpenAI API calls...")
    
    start_time = time.time()
    
    def simulate_api_call(call_id: int, duration: float = 1.0):
        """Simulate a single API call"""
        logger.info(f"Starting concurrent API call {call_id}")
        time.sleep(duration)  # Simulate API call latency
        logger.info(f"Completed concurrent API call {call_id}")
        return f"Result from call {call_id}"
    
    # Simulate concurrent execution using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all 9 API calls concurrently
        futures = []
        for i in range(9):
            future = executor.submit(simulate_api_call, i+1)
            futures.append(future)
        
        # Wait for all calls to complete
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"API call failed: {e}")
    
    end_time = time.time()
    concurrent_time = end_time - start_time
    
    logger.info(f"Concurrent execution completed in {concurrent_time:.2f} seconds")
    return concurrent_time

def main():
    """Run the performance comparison"""
    logger.info("=== OpenAI API Call Performance Comparison ===")
    logger.info("Comparing sequential vs concurrent execution")
    logger.info("")
    
    # Test sequential execution
    sequential_time = simulate_sequential_openai_calls()
    
    logger.info("")
    logger.info("-" * 50)
    logger.info("")
    
    # Test concurrent execution
    concurrent_time = simulate_concurrent_openai_calls()
    
    logger.info("")
    logger.info("=== PERFORMANCE COMPARISON RESULTS ===")
    logger.info(f"Sequential execution time: {sequential_time:.2f} seconds")
    logger.info(f"Concurrent execution time: {concurrent_time:.2f} seconds")
    
    if concurrent_time > 0:
        speedup = sequential_time / concurrent_time
        time_saved = sequential_time - concurrent_time
        logger.info(f"Speedup factor: {speedup:.2f}x")
        logger.info(f"Time saved: {time_saved:.2f} seconds")
        logger.info(f"Performance improvement: {((speedup - 1) * 100):.1f}%")
    
    logger.info("")
    logger.info("=== REAL-WORLD IMPACT ===")
    logger.info("In the financial dashboard application:")
    logger.info("- Sequential: Each OpenAI API call waits for the previous one")
    logger.info("- Concurrent: All OpenAI API calls run simultaneously")
    logger.info("- Result: Faster dashboard generation and better user experience")

if __name__ == "__main__":
    main()
