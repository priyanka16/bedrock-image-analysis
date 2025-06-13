#!/usr/bin/env python
"""
Test script for the enhanced logging system
"""

import sys
import time
import random
from pathlib import Path
import os

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.logger_config import setup_logging, get_logger, get_performance_logger

def test_basic_logging():
    """Test basic logging functionality"""
    logger = get_logger("test_basic")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    try:
        # Generate an exception
        1 / 0
    except Exception as e:
        logger.error("This is an error with exception", exc_info=True)

def test_performance_logging():
    """Test performance logging functionality"""
    logger = get_performance_logger("test_performance")
    
    # Test with a simple operation
    logger.start_timer("simple_operation")
    time.sleep(0.5)  # Simulate work
    logger.stop_timer("simple_operation", message="Completed simple operation")
    
    # Test with a longer operation
    logger.start_timer("complex_operation")
    time.sleep(1.2)  # Simulate more complex work
    logger.stop_timer("complex_operation", message="Completed complex operation")
    
    # Test with random durations
    for i in range(5):
        operation = f"random_operation_{i}"
        logger.start_timer(operation)
        time.sleep(random.uniform(0.1, 0.8))  # Random duration
        logger.stop_timer(operation, message=f"Completed random operation {i}")

def test_request_logging():
    """Test request-specific logging"""
    from utils.logger_config import get_request_logger
    
    # Simulate a few requests
    for i in range(3):
        request_id = f"req-{random.randint(1000, 9999)}"
        user_id = f"user-{random.randint(100, 999)}"
        
        logger = get_request_logger("test_request", request_id=request_id, user_id=user_id)
        
        logger.info(f"Processing request {i+1}")
        
        # Simulate different outcomes
        if i == 0:
            logger.info("Request processed successfully")
        elif i == 1:
            logger.warning("Request processed with warnings")
        else:
            logger.error("Request processing failed")

def main():
    """Main function"""
    # Initialize logging with config
    setup_logging()
    
    print("Running logging tests...")
    
    # Run tests
    test_basic_logging()
    test_performance_logging()
    test_request_logging()
    
    # Print log file location
    log_dir = Path(__file__).parent / "logs"
    log_files = list(log_dir.glob("*.log*"))
    
    print(f"\nTest complete. Generated {len(log_files)} log files in {log_dir}")
    for log_file in log_files:
        print(f" - {log_file.name} ({os.path.getsize(log_file) / 1024:.1f} KB)")
    
    print("\nYou can analyze these logs with:")
    print(f"python scripts/monitor_logs.py --log-dir {log_dir}")

if __name__ == "__main__":
    main()
