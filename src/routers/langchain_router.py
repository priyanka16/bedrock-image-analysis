"""
FastAPI router for LangChain image analysis endpoints using latest implementations
"""

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
import os
import time
import uuid

from utils.image_utils import save_uploaded_image, create_image_data_dict
from services.image_analysis import analyze_image_basic, analyze_image_structured, analyze_image_specialized
from config.langchain_config import PROMPTS
from utils.logger_config import get_logger

# Get logger for this module
logger = get_logger("langchain_router")

# Create router
router = APIRouter(tags=["Image Analysis"])

# Temporary image storage path
TEMP_IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/temp")

@router.get("/health")
async def health_check(request: Request = None):
    """Health check endpoint for LangChain router"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    logger.info("LangChain health check", extra={"request_id": request_id})
    return {
        "status": "healthy", 
        "service": "langchain-image-analysis", 
        "version": "2.0.0",
        "request_id": request_id
    }

@router.get("/prompts")
async def list_prompts(request: Request = None):
    """List available analysis prompt types"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    logger.info("Listing available prompt types", extra={"request_id": request_id})
    logger.debug(f"Available prompts: {list(PROMPTS.keys())}", extra={"request_id": request_id})
    return {
        "prompts": list(PROMPTS.keys()), 
        "count": len(PROMPTS),
        "request_id": request_id
    }

@router.post("/analyze/basic")
async def analyze_image_basic_endpoint(file: UploadFile = File(...), request: Request = None):
    """
    Analyze an image using the basic LangChain analysis
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"Basic analysis requested for file: {file.filename}", extra={"request_id": request_id})
    
    try:
        # Save the uploaded file temporarily
        logger.debug(f"Saving uploaded file to temp directory", extra={"request_id": request_id})
        file_path = save_uploaded_image(file, TEMP_IMAGE_DIR, request_id=request_id)
        logger.debug(f"File saved at: {file_path}", extra={"request_id": request_id})
        
        # Process with basic analysis
        logger.info(f"Processing image with basic analysis", extra={"request_id": request_id})
        result = analyze_image_basic(file_path, request_id)
        
        # Add image metadata to result
        if result.get("success"):
            result["image"] = create_image_data_dict(file_path, request_id)
            result["processing_time"] = round(time.time() - start_time, 2)
        
        # Clean up the temporary file
        logger.debug(f"Removing temporary file: {file_path}", extra={"request_id": request_id})
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Basic analysis completed successfully in {result.get('processing_time', 0)}s", 
                  extra={"request_id": request_id})
        
        return JSONResponse(content=result)
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        logger.error(f"Error in basic analysis: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return JSONResponse(
            content={
                "success": False, 
                "error": str(e), 
                "request_id": request_id,
                "processing_time": processing_time
            },
            status_code=500
        )

@router.post("/analyze/structured")
async def analyze_image_structured_endpoint(file: UploadFile = File(...), request: Request = None):
    """
    Analyze an image using the structured LangChain analysis that returns JSON
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"Structured analysis requested for file: {file.filename}", extra={"request_id": request_id})
    
    try:
        # Save the uploaded file temporarily
        logger.debug(f"Saving uploaded file to temp directory", extra={"request_id": request_id})
        file_path = save_uploaded_image(file, TEMP_IMAGE_DIR, request_id=request_id)
        logger.debug(f"File saved at: {file_path}", extra={"request_id": request_id})
        
        # Process with structured analysis
        logger.info(f"Processing image with structured analysis", extra={"request_id": request_id})
        result = analyze_image_structured(file_path, request_id)
        
        # Add image metadata to result
        if result.get("success"):
            result["image"] = create_image_data_dict(file_path, request_id)
            result["processing_time"] = round(time.time() - start_time, 2)
        
        # Clean up the temporary file
        logger.debug(f"Removing temporary file: {file_path}", extra={"request_id": request_id})
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Structured analysis completed successfully in {result.get('processing_time', 0)}s", 
                  extra={"request_id": request_id})
        
        return JSONResponse(content=result)
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        logger.error(f"Error in structured analysis: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return JSONResponse(
            content={
                "success": False, 
                "error": str(e), 
                "request_id": request_id,
                "processing_time": processing_time
            },
            status_code=500
        )

@router.post("/analyze/specialized")
async def analyze_image_specialized_endpoint(
    file: UploadFile = File(...),
    analysis_type: str = Form(...),
    request: Request = None
):
    """
    Analyze an image using a specialized LangChain analysis
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"Specialized analysis requested for file: {file.filename}, type: {analysis_type}", 
                extra={"request_id": request_id})
    
    if analysis_type not in PROMPTS:
        logger.warning(f"Invalid analysis type requested: {analysis_type}", extra={"request_id": request_id})
        valid_types = list(PROMPTS.keys())
        return JSONResponse(
            content={
                "success": False, 
                "error": f"Invalid analysis_type. Valid options: {valid_types}",
                "valid_types": valid_types,
                "request_id": request_id
            },
            status_code=400
        )
    
    try:
        # Save the uploaded file temporarily
        logger.debug(f"Saving uploaded file to temp directory", extra={"request_id": request_id})
        file_path = save_uploaded_image(file, TEMP_IMAGE_DIR, request_id=request_id)
        logger.debug(f"File saved at: {file_path}", extra={"request_id": request_id})
        
        # Process with specialized analysis
        logger.info(f"Processing image with specialized analysis: {analysis_type}", extra={"request_id": request_id})
        result = analyze_image_specialized(file_path, analysis_type, request_id)
        
        # Add image metadata to result
        if result.get("success"):
            result["image"] = create_image_data_dict(file_path, request_id)
            result["processing_time"] = round(time.time() - start_time, 2)
        
        # Clean up the temporary file
        logger.debug(f"Removing temporary file: {file_path}", extra={"request_id": request_id})
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Specialized analysis ({analysis_type}) completed successfully in {result.get('processing_time', 0)}s", 
                  extra={"request_id": request_id})
        
        return JSONResponse(content=result)
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        logger.error(f"Error in specialized analysis: {str(e)}", 
                    extra={"request_id": request_id, "analysis_type": analysis_type}, 
                    exc_info=True)
        return JSONResponse(
            content={
                "success": False, 
                "error": str(e), 
                "request_id": request_id,
                "processing_time": processing_time,
                "analysis_type": analysis_type
            },
            status_code=500
        )
