"""
Utility functions for image processing and handling
"""

import os
import base64
import time
from typing import Optional, Dict, Any

from utils.logger_config import get_logger

# Get logger for this module
logger = get_logger("image_utils")

def encode_image_to_base64(image_path: str, request_id: Optional[str] = None) -> str:
    """Encode an image file to base64 string"""
    start_time = time.time()
    logger.debug(f"Encoding image to base64: {image_path}", extra={"request_id": request_id})
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}", extra={"request_id": request_id})
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read file and encode
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
            img_size_kb = len(img_bytes) / 1024
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            
        encoding_time = time.time() - start_time
        logger.debug(f"Image encoded successfully: {os.path.basename(image_path)}, " + 
                    f"size: {img_size_kb:.2f}KB, time: {encoding_time:.3f}s", 
                    extra={"request_id": request_id})
        return img_b64
        
    except Exception as e:
        logger.error(f"Error encoding image to base64: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        raise

def get_image_mime_type(image_path: str, request_id: Optional[str] = None) -> str:
    """Determine the MIME type of an image based on file extension"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')  # Default to JPEG if unknown
    
    if ext and ext not in mime_types:
        logger.warning(f"Unknown image extension: {ext}, defaulting to image/jpeg", 
                     extra={"request_id": request_id})
    
    logger.debug(f"Detected MIME type for {os.path.basename(image_path)}: {mime_type}", 
                extra={"request_id": request_id})
    return mime_type

def save_uploaded_image(uploaded_file, destination_folder: str, filename: Optional[str] = None, 
                     request_id: Optional[str] = None) -> str:
    """Save an uploaded file to the specified destination folder"""
    start_time = time.time()
    logger.info(f"Saving uploaded image: {uploaded_file.filename}", extra={"request_id": request_id})
    
    try:
        # Create destination folder if it doesn't exist
        logger.debug(f"Creating destination folder if needed: {destination_folder}", 
                    extra={"request_id": request_id})
        os.makedirs(destination_folder, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            file_ext = os.path.splitext(uploaded_file.filename)[1]
            filename = f"uploaded_image_{os.urandom(4).hex()}{file_ext}"
            logger.debug(f"Generated filename: {filename}", extra={"request_id": request_id})
        
        # Full path to save the file
        file_path = os.path.join(destination_folder, filename)
        logger.debug(f"Saving to: {file_path}", extra={"request_id": request_id})
        
        # Save the file
        with open(file_path, "wb") as buffer:
            file_content = uploaded_file.file.read()
            buffer.write(file_content)
            file_size_kb = len(file_content) / 1024
        
        save_time = time.time() - start_time
        logger.info(f"Saved uploaded image to {file_path}, size: {file_size_kb:.2f}KB, " +
                   f"time: {save_time:.3f}s", extra={"request_id": request_id})
        return file_path
    
    except Exception as e:
        logger.error(f"Error saving uploaded image: {str(e)}", 
                    extra={"request_id": request_id}, exc_info=True)
        raise

def create_image_data_dict(image_path: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a dictionary with image data for API responses"""
    logger.debug(f"Creating image data dictionary for: {image_path}", extra={"request_id": request_id})
    
    try:
        # Get file stats
        file_stats = os.stat(image_path)
        file_name = os.path.basename(image_path)
        file_size_kb = file_stats.st_size / 1024
        mime_type = get_image_mime_type(image_path, request_id)
        
        # Create response dict
        image_data = {
            "file_name": file_name,
            "file_size_kb": round(file_size_kb, 2),
            "mime_type": mime_type,
            "file_path": image_path,
            "last_modified": file_stats.st_mtime
        }
        
        logger.debug(f"Image data created for {file_name}, size: {file_size_kb:.2f}KB", 
                    extra={"request_id": request_id})
        return image_data
        
    except Exception as e:
        logger.error(f"Error creating image data dict: {str(e)}", 
                    extra={"request_id": request_id}, exc_info=True)
        return {
            "file_name": os.path.basename(image_path),
            "error": str(e)
        }
