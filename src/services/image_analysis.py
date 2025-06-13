"""
Consolidated image analysis service using latest LangChain implementations with AWS Bedrock
"""

import base64
import json
import time
import os
from typing import Dict, Any, Optional, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from pydantic import BaseModel, Field

from config.langchain_config import BEDROCK_MODELS, MODEL_SETTINGS, AWS_REGION, PROMPTS
from utils.logger_config import get_logger

# Get logger for this module
logger = get_logger("image_analysis")

class ImageAnalysisResult(BaseModel):
    """Schema for structured image analysis results"""
    description: str = Field(description="General description of the image")
    objects: List[str] = Field(description="List of objects identified in the image")
    setting: str = Field(description="The setting or context of the image")
    text_content: Optional[str] = Field(None, description="Any text content visible in the image")
    colors: List[str] = Field(description="Dominant colors in the image")
    style: str = Field(description="Visual style of the image")
    confidence: float = Field(description="Confidence score for the analysis", ge=0.0, le=1.0)

def get_bedrock_llm(model_type: str = "claude_sonnet") -> ChatBedrock:
    """Create and return a LangChain Bedrock chat model with latest configuration"""
    model_id = BEDROCK_MODELS.get(model_type, BEDROCK_MODELS["claude_sonnet"])
    model_kwargs = MODEL_SETTINGS.get(model_type, MODEL_SETTINGS["claude_sonnet"])
    
    logger.info(f"Initializing Bedrock LLM with model: {model_id}")
    
    try:
        llm = ChatBedrock(
            model_id=model_id,
            model_kwargs=model_kwargs,
            region_name=AWS_REGION,
        )
        logger.debug("Bedrock LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock LLM: {str(e)}", exc_info=True)
        raise

def create_multimodal_message(image_path: str, prompt_text: str, request_id: Optional[str] = None) -> HumanMessage:
    """Create a multimodal message with text and image for Claude"""
    try:
        logger.info(f"Creating multimodal message for image: {os.path.basename(image_path)}", 
                   extra={"request_id": request_id})
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}", extra={"request_id": request_id})
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read and base64 encode the image
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
            img_size_kb = len(img_bytes) / 1024
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            
        logger.debug(f"Image encoded successfully: size: {img_size_kb:.2f}KB", 
                    extra={"request_id": request_id})
    
        # Create multimodal message
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}"
                    }
                }
            ]
        )
        logger.debug(f"Multimodal message created with prompt: '{prompt_text[:50]}...'", 
                    extra={"request_id": request_id})
        return message
    except Exception as e:
        logger.error(f"Error creating multimodal message: {str(e)}", 
                    extra={"request_id": request_id}, exc_info=True)
        raise

def analyze_image_basic(image_path: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an image using basic LangChain implementation with latest patterns"""
    function_start_time = time.time()
    if not request_id:
        request_id = f"req_{int(function_start_time * 1000) % 10000:04d}"
    
    logger.info(f"Starting basic image analysis for: {os.path.basename(image_path)}", 
               extra={"request_id": request_id})
    
    try:
        # Create the multimodal message
        prompt = PROMPTS["basic_analysis"]
        message = create_multimodal_message(image_path, prompt, request_id)
        
        # Use latest LangChain pattern with ChatBedrock
        llm = get_bedrock_llm()
        
        # Create system message for context
        system_message = SystemMessage(content="You are an expert image analyst. Provide detailed descriptions of images.")
        
        # Process with the model
        logger.info(f"Invoking Bedrock model for basic analysis", extra={"request_id": request_id})
        start_time = time.time()
        response = llm.invoke([system_message, message])
        inference_time = time.time() - start_time
        
        result = response.content
        
        # Log result preview
        result_preview = result[:100] + "..." if len(result) > 100 else result
        logger.info(f"Basic analysis completed in {inference_time:.2f}s. Result: {result_preview}", 
                   extra={"request_id": request_id})
        
        # Format response
        total_time = time.time() - function_start_time
        response_data = {
            "success": True, 
            "result": result,
            "analysis_type": "basic",
            "metrics": {
                "total_time_seconds": round(total_time, 2),
                "inference_time_seconds": round(inference_time, 2)
            },
            "request_id": request_id
        }
        return response_data
        
    except Exception as e:
        logger.error(f"Error in basic image analysis: {str(e)}", 
                    extra={"request_id": request_id}, exc_info=True)
        total_time = time.time() - function_start_time
        return {
            "success": False, 
            "error": str(e), 
            "request_id": request_id,
            "metrics": {"total_time_seconds": round(total_time, 2)}
        }

def analyze_image_structured(image_path: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an image and return structured JSON results using latest LangChain patterns"""
    function_start_time = time.time()
    if not request_id:
        request_id = f"req_{int(function_start_time * 1000) % 10000:04d}"
    
    logger.info(f"Starting structured image analysis for: {os.path.basename(image_path)}", 
               extra={"request_id": request_id})
    
    try:
        # Create the multimodal message with structured prompt
        structured_prompt = """Analyze this image and return a JSON object with the following fields:
        - description: General description of the image
        - objects: List of objects identified in the image
        - setting: The setting or context of the image
        - text_content: Any text content visible in the image (null if none)
        - colors: Dominant colors in the image
        - style: Visual style of the image
        - confidence: Confidence score for the analysis (0.0 to 1.0)
        
        Return only valid JSON without any explanations or markdown formatting."""
        
        message = create_multimodal_message(image_path, structured_prompt, request_id)
        
        # Use latest LangChain pattern with structured output
        llm = get_bedrock_llm()
        
        # Create system message for structured analysis
        system_message = SystemMessage(content="You are an expert image analyst. Return only valid JSON responses as requested.")
        
        # Process with the model
        logger.info(f"Invoking Bedrock model for structured analysis", extra={"request_id": request_id})
        start_time = time.time()
        response = llm.invoke([system_message, message])
        inference_time = time.time() - start_time
        
        # Parse JSON response
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
        
        logger.info(f"Structured analysis completed in {inference_time:.2f}s", 
                   extra={"request_id": request_id})
        
        # Format response
        total_time = time.time() - function_start_time
        response_data = {
            "success": True, 
            "result": result,
            "analysis_type": "structured",
            "metrics": {
                "total_time_seconds": round(total_time, 2),
                "inference_time_seconds": round(inference_time, 2)
            },
            "request_id": request_id
        }
        return response_data
        
    except Exception as e:
        logger.error(f"Error in structured image analysis: {str(e)}", 
                    extra={"request_id": request_id}, exc_info=True)
        total_time = time.time() - function_start_time
        return {
            "success": False, 
            "error": str(e), 
            "request_id": request_id,
            "metrics": {"total_time_seconds": round(total_time, 2)}
        }

def analyze_image_specialized(image_path: str, analysis_type: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an image using specialized prompts and latest LangChain patterns"""
    function_start_time = time.time()
    if not request_id:
        request_id = f"req_{int(function_start_time * 1000) % 10000:04d}"
    
    logger.info(f"Starting specialized image analysis ({analysis_type}) for: {os.path.basename(image_path)}", 
               extra={"request_id": request_id, "analysis_type": analysis_type})
    
    # Validate analysis type
    if analysis_type not in PROMPTS:
        error_msg = f"Invalid analysis_type: {analysis_type}. Valid options: {list(PROMPTS.keys())}"
        logger.error(error_msg, extra={"request_id": request_id})
        return {
            "success": False, 
            "error": error_msg, 
            "request_id": request_id
        }
    
    try:
        # Get specialized prompt
        prompt = PROMPTS[analysis_type]
        message = create_multimodal_message(image_path, prompt, request_id)
        
        # Use latest LangChain pattern
        llm = get_bedrock_llm()
        
        # Create specialized system messages
        system_prompts = {
            "object_detection": "You are an expert in object detection. Identify and count all objects in the image with high precision.",
            "text_recognition": "You are an expert in text recognition and OCR. Extract and transcribe any text in the image accurately.",
            "scene_analysis": "You are an expert in scene analysis. Describe the setting, context, and environment shown in the image in detail.",
            "advanced_analysis": "You are a comprehensive image analyst. Provide detailed analysis of all aspects of the image including objects, scene, text, style, and emotional context."
        }
        
        system_content = system_prompts.get(analysis_type, "You are an expert image analyst.")
        system_message = SystemMessage(content=system_content)
        
        # Process with the model
        logger.info(f"Invoking Bedrock model for specialized analysis: {analysis_type}", 
                   extra={"request_id": request_id})
        start_time = time.time()
        response = llm.invoke([system_message, message])
        inference_time = time.time() - start_time
        
        result = response.content
        
        # Log result preview
        result_preview = result[:100] + "..." if len(result) > 100 else result
        logger.info(f"Specialized analysis ({analysis_type}) completed in {inference_time:.2f}s. Result: {result_preview}", 
                   extra={"request_id": request_id})
        
        # Format response
        total_time = time.time() - function_start_time
        response_data = {
            "success": True, 
            "result": result,
            "analysis_type": analysis_type,
            "metrics": {
                "total_time_seconds": round(total_time, 2),
                "inference_time_seconds": round(inference_time, 2)
            },
            "request_id": request_id
        }
        return response_data
        
    except Exception as e:
        logger.error(f"Error in specialized image analysis ({analysis_type}): {str(e)}", 
                    extra={"request_id": request_id, "analysis_type": analysis_type}, exc_info=True)
        total_time = time.time() - function_start_time
        return {
            "success": False, 
            "error": str(e), 
            "analysis_type": analysis_type,
            "request_id": request_id,
            "metrics": {"total_time_seconds": round(total_time, 2)}
        }

if __name__ == "__main__":
    # Example usage
    image_path = "data/images/sample_image1.jpg"
    
    is_enable_basic = False
    is_enable_structured = True
    is_enable_specialized = False
    
    if not os.path.exists(image_path):
        print(f"Image file does not exist: {image_path}")
        exit(1)
    
    if is_enable_basic:
        print("Running basic image analysis...")
        # Basic analysis
        basic_result = analyze_image_basic(image_path)
        print("Basic Analysis Result:", basic_result)
    
    if is_enable_structured:
        print("Running structured image analysis...")
        
        # Structured analysis
        structured_result = analyze_image_structured(image_path)
        print("Structured Analysis Result:", structured_result)
    
    if is_enable_specialized:
        print("Running specialized image analysis...")
        
        # Specialized analysis types
        specialized_types = ["object_detection", "text_recognition", "scene_analysis", "advanced_analysis"]
        for analysis_type in specialized_types:
            print(f"Running {analysis_type} analysis...")
            specialized_result = analyze_image_specialized(image_path, analysis_type)
            print(f"{analysis_type.capitalize()} Analysis Result:", specialized_result)
