"""
Main entry point for the Image Analysis API using LangChain and AWS Bedrock
This is the primary server file with all endpoints organized through routers.
"""

import os
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from routers.langchain_router import router as langchain_router
from utils.logger_config import setup_logging, get_logger

# Create logs directory
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
setup_logging({
    "general": {
        "app_name": "image_analysis",
        "default_level": "info"
    },
    "file": {
        "enabled": True,
        "directory": logs_dir,
        "format": "standard"
    }
})
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Image Analysis API with LangChain and AWS Bedrock",
    description="Advanced image analysis using AWS Bedrock Claude models with LangChain integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request ID middleware for tracking requests
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"Request started: {request.method} {request.url.path}", extra={"request_id": request_id})
    
    try:
        response = await call_next(request)
        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}", 
                   extra={"request_id": request_id})
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}", 
                    extra={"request_id": request_id})
        raise

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(langchain_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Image Analysis API with LangChain and AWS Bedrock",
        "description": "Advanced image analysis using AWS Bedrock Claude models with LangChain integration",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "langchain_health": "/api/v1/health",
            "prompts": "/api/v1/prompts",
            "basic_analysis": "/api/v1/analyze/basic",
            "structured_analysis": "/api/v1/analyze/structured", 
            "specialized_analysis": "/api/v1/analyze/specialized"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "version": "2.0.0",
        "service": "image-analysis-api"
    }

if __name__ == "__main__":
    try:
        logger.info("="*50)
        logger.info("Starting Image Analysis API server")
        logger.info(f"Environment: Development")
        logger.info(f"Log directory: {logs_dir}")
        logger.info(f"Server port: 8000")
        logger.info("="*50)
        
        # Check for AWS credentials
        if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get("AWS_SECRET_ACCESS_KEY"):
            logger.warning("AWS credentials not found in environment variables")
            logger.warning("Make sure AWS credentials are properly configured for Bedrock access")
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
