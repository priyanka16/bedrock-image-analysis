#!/usr/bin/env python3
"""
Script to test LangChain image analysis functionality directly
"""

import os
import json
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the Python environment and import necessary modules"""
    try:
        # Add the src directory to the Python path
        import sys
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(script_dir, "src")
        sys.path.append(src_dir)
        
        # Import updated modules
        from services.image_analysis import analyze_image_basic, analyze_image_structured, analyze_image_specialized
        from config.langchain_config import PROMPTS
        
        return True
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        logger.error("Make sure you've activated your virtual environment and installed all dependencies")
        return False

def test_basic_analysis(image_path):
    """Test basic image analysis with LangChain"""
    from services.image_analysis import analyze_image_basic
    
    logger.info(f"Running basic analysis on {image_path}")
    result = analyze_image_basic(image_path)
    
    print("\n===== BASIC ANALYSIS =====")
    if result["success"]:
        print(result["result"])
        if "metrics" in result:
            print(f"\nProcessing time: {result['metrics']['total_time_seconds']}s")
    else:
        print(f"Error: {result['error']}")

def test_structured_analysis(image_path):
    """Test structured image analysis with LangChain"""
    from services.image_analysis import analyze_image_structured
    
    logger.info(f"Running structured analysis on {image_path}")
    result = analyze_image_structured(image_path)
    
    print("\n===== STRUCTURED ANALYSIS =====")
    if result["success"]:
        try:
            # Display the structured result
            if isinstance(result["result"], dict):
                print(json.dumps(result["result"], indent=2))
            else:
                print(result["result"])
            if "metrics" in result:
                print(f"\nProcessing time: {result['metrics']['total_time_seconds']}s")
        except Exception as e:
            print(f"Error displaying result: {e}")
            print(result["result"])
    else:
        print(f"Error: {result['error']}")

def test_specialized_analysis(image_path, analysis_type):
    """Test specialized image analysis with LangChain"""
    from services.image_analysis import analyze_image_specialized
    from config.langchain_config import PROMPTS
    
    if analysis_type not in PROMPTS:
        print(f"Error: Invalid analysis type '{analysis_type}'")
        print(f"Available types: {list(PROMPTS.keys())}")
        return
    
    logger.info(f"Running {analysis_type} analysis on {image_path}")
    result = analyze_image_specialized(image_path, analysis_type)
    
    print(f"\n===== {analysis_type.upper()} ANALYSIS =====")
    if result["success"]:
        print(result["result"])
        if "metrics" in result:
            print(f"\nProcessing time: {result['metrics']['total_time_seconds']}s")
    else:
        print(f"Error: {result['error']}")

def list_available_analysis_types():
    """List all available analysis types"""
    from config.langchain_config import PROMPTS
    
    print("\n===== AVAILABLE ANALYSIS TYPES =====")
    for analysis_type, prompt in PROMPTS.items():
        print(f"- {analysis_type}")
        print(f"  {prompt[:100]}...")
        print()

def main():
    """Main function to run the test script"""
    parser = argparse.ArgumentParser(description="Test LangChain image analysis functionality")
    parser.add_argument("image_path", nargs='?', help="Path to the image file to analyze")
    parser.add_argument("--type", choices=["basic", "structured", "specialized"], default="basic",
                        help="Type of analysis to perform")
    parser.add_argument("--analysis", help="Specialized analysis type (for --type=specialized)")
    parser.add_argument("--list-types", action="store_true", help="List available analysis types")
    args = parser.parse_args()
    
    # Set up the environment
    if not setup_environment():
        return
    
    # List analysis types if requested
    if args.list_types:
        list_available_analysis_types()
        return
    
    # Check if image path is provided
    if not args.image_path:
        logger.error("Please provide an image path or use --list-types to see available analysis types")
        return
    
    # Check if the image file exists
    if not os.path.isfile(args.image_path):
        logger.error(f"Image file not found: {args.image_path}")
        return
    
    # Run the requested analysis
    try:
        if args.type == "basic":
            test_basic_analysis(args.image_path)
        elif args.type == "structured":
            test_structured_analysis(args.image_path)
        elif args.type == "specialized":
            if not args.analysis:
                logger.error("Please specify an analysis type with --analysis")
                logger.info("Use --list-types to see available analysis types")
                return
            test_specialized_analysis(args.image_path, args.analysis)
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()
