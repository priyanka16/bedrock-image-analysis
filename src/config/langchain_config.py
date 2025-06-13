"""
Configuration settings for LangChain integrations with latest model versions and best practices
"""
import os
from utils.logger_config import get_logger

# Set up logger for this module
logger = get_logger("langchain_config")

# Log configuration loading
logger.info("Loading LangChain configuration")

# AWS Bedrock models configuration with latest versions
BEDROCK_MODELS = {
    "claude_sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0", # Claude 3 Sonnet 
    "claude_haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0", # Claude 3 Haiku (fast, cost-effective)
    "claude_opus": "us.anthropic.claude-3-opus-20240229-v1:0",       # Claude 3 Opus (most capable)
}

# LangChain model settings optimized for image analysis
MODEL_SETTINGS = {
    "claude_sonnet": {
        "max_tokens": 4000,
        "temperature": 0.1,  # Lower temperature for more consistent analysis
        "top_p": 0.9,
        "top_k": 250,
        "stop_sequences": [],
    },
    "claude_haiku": {
        "max_tokens": 2000,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 250,
        "stop_sequences": [],
    },
    "claude_opus": {
        "max_tokens": 4000,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 250,
        "stop_sequences": [],
    }
}

# Region configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
logger.debug(f"Using AWS region: {AWS_REGION}")

# Enhanced analysis prompts with better specificity
PROMPTS = {
    "basic_analysis": """Analyze this image and provide a comprehensive description. Include:
    1. Main subjects and objects in the image
    2. Setting and environment
    3. Colors, lighting, and visual composition
    4. Any notable details or interesting elements
    
    Provide a detailed but concise analysis.""",
    
    "object_detection": """Identify and count all objects visible in this image. For each object:
    1. Name the object
    2. Describe its location in the image
    3. Note its size relative to other objects
    4. Mention any distinctive features
    
    Be thorough and systematic in your identification.""",
    
    "text_recognition": """Extract and transcribe any text visible in this image. Include:
    1. All readable text, maintaining original formatting where possible
    2. Description of text style, font, and appearance
    3. Location of text within the image
    4. Language of the text if not English
    5. Any partially visible or unclear text with your best interpretation
    
    If no text is visible, clearly state "No readable text found in the image".""",
    
    "scene_analysis": """Analyze the scene and context of this image. Provide:
    1. Type of location/setting (indoor/outdoor, specific venue type)
    2. Time of day and lighting conditions
    3. Weather conditions (if outdoor)
    4. Mood and atmosphere of the scene
    5. Cultural or geographical context if identifiable
    6. Any activities or events taking place
    
    Focus on environmental and contextual details.""",
    
    "advanced_analysis": """Provide a comprehensive analysis of this image covering all aspects:
    
    **Visual Elements:**
    - Objects, people, and subjects present
    - Composition, framing, and visual hierarchy
    - Colors, lighting, and photographic techniques
    
    **Context and Setting:**
    - Location type and environmental details
    - Time period indicators and cultural context
    - Activities or events depicted
    
    **Technical Aspects:**
    - Image quality and style
    - Any visible text or signage
    - Artistic or documentary qualities
    
    **Interpretation:**
    - Emotional tone or mood conveyed
    - Potential purpose or intent of the image
    - Notable or unusual elements
    
    Provide detailed insights while maintaining objectivity.""",
    
    "artistic_analysis": """Analyze this image from an artistic and aesthetic perspective:
    1. Composition techniques (rule of thirds, leading lines, symmetry, etc.)
    2. Color palette and color theory application
    3. Lighting techniques and mood creation
    4. Visual style and artistic movement influences
    5. Emotional impact and artistic intent
    6. Technical execution and craftsmanship
    
    Focus on the artistic and creative aspects of the image.""",
    
    "technical_analysis": """Provide a technical analysis of this image:
    1. Image quality, resolution, and clarity
    2. Photographic techniques used (depth of field, exposure, etc.)
    3. Equipment or camera settings that might have been used
    4. Post-processing or editing evidence
    5. File format considerations and compression artifacts
    6. Technical strengths and weaknesses
    
    Focus on the technical and photographic aspects."""
}

# Model performance characteristics for selection guidance
MODEL_CHARACTERISTICS = {
    "claude_sonnet": {
        "speed": "fast",
        "cost": "medium",
        "capability": "high",
        "best_for": ["general_analysis", "structured_output", "detailed_descriptions"],
        "max_image_size_mb": 5
    },
    "claude_haiku": {
        "speed": "very_fast", 
        "cost": "low",
        "capability": "medium",
        "best_for": ["quick_analysis", "object_detection", "simple_tasks"],
        "max_image_size_mb": 5
    },
    "claude_opus": {
        "speed": "slow",
        "cost": "high", 
        "capability": "very_high",
        "best_for": ["complex_analysis", "artistic_interpretation", "detailed_reasoning"],
        "max_image_size_mb": 5
    }
}

# Default model selection based on analysis type
DEFAULT_MODEL_FOR_ANALYSIS = {
    "basic_analysis": "claude_sonnet",
    "object_detection": "claude_haiku",
    "text_recognition": "claude_sonnet", 
    "scene_analysis": "claude_sonnet",
    "advanced_analysis": "claude_opus",
    "artistic_analysis": "claude_opus",
    "technical_analysis": "claude_sonnet"
}

# Validation settings
MAX_IMAGE_SIZE_MB = 5
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
MIN_IMAGE_DIMENSION = 32  # pixels
MAX_IMAGE_DIMENSION = 8192  # pixels

# Rate limiting and retry settings
RATE_LIMIT_SETTINGS = {
    "max_requests_per_minute": 60,
    "max_concurrent_requests": 10,
    "retry_attempts": 3,
    "retry_delay_seconds": 1,
    "backoff_multiplier": 2
}

# Response formatting settings
RESPONSE_SETTINGS = {
    "include_confidence_scores": True,
    "include_processing_metrics": True,
    "include_model_info": True,
    "max_response_length": 10000,
    "truncate_long_responses": True
}

def get_recommended_model(analysis_type: str) -> str:
    """Get the recommended model for a specific analysis type"""
    return DEFAULT_MODEL_FOR_ANALYSIS.get(analysis_type, "claude_sonnet")

def validate_image_specs(file_size_mb: float, width: int, height: int, format_ext: str) -> tuple[bool, str]:
    """Validate image specifications against limits"""
    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"Image size {file_size_mb:.1f}MB exceeds maximum of {MAX_IMAGE_SIZE_MB}MB"
    
    if format_ext.lower() not in SUPPORTED_IMAGE_FORMATS:
        return False, f"Image format {format_ext} not supported. Supported formats: {SUPPORTED_IMAGE_FORMATS}"
    
    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        return False, f"Image dimensions {width}x{height} too small. Minimum: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}"
    
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        return False, f"Image dimensions {width}x{height} too large. Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}"
    
    return True, "Image specifications valid"

logger.info(f"LangChain configuration loaded successfully:")
logger.info(f"  - {len(PROMPTS)} prompt types available")
logger.info(f"  - {len(BEDROCK_MODELS)} models configured")
logger.info(f"  - AWS Region: {AWS_REGION}")
logger.info(f"  - Max image size: {MAX_IMAGE_SIZE_MB}MB")
logger.info(f"  - Supported formats: {SUPPORTED_IMAGE_FORMATS}")
