"""
Centralized logging configuration for the image analysis application
"""

import logging
import os
import sys
import json
import yaml
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Log levels dictionary for configuration
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
# Format for JSON logs
JSON_LOG_FORMAT = '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}'
# Simple format
SIMPLE_LOG_FORMAT = '%(levelname)s - %(message)s'

# Time rotation options
TIME_ROTATION_OPTIONS = {
    "S": "seconds",
    "M": "minutes",
    "H": "hours",
    "D": "days",
    "midnight": "midnight"
}

class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON objects"""
    
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "file": record.filename,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Add any extra attributes
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
            
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
            
        # Add performance metrics if present
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
            
        if hasattr(record, "memory_usage"):
            log_record["memory_usage"] = record.memory_usage
            
        return json.dumps(log_record)

def get_config():
    """
    Load logging configuration from YAML file
    
    Returns:
        dict: Configuration dictionary
    """
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "logging_config.yaml"
    
    # Default configuration
    default_config = {
        "general": {
            "app_name": "image_analysis",
            "default_level": "info"
        },
        "console": {
            "enabled": True,
            "level": "info",
            "format": "standard"
        },
        "file": {
            "enabled": True,
            "level": "debug",
            "format": "json",
            "directory": "logs",
            "rotation": {
                "enabled": True,
                "max_size_mb": 10,
                "backup_count": 5,
                "when": "midnight",
                "interval": 1
            }
        },
        "metrics": {
            "enabled": True,
            "include_memory": True,
            "include_cpu": False
        },
        "request_tracking": {
            "enabled": True,
            "include_headers": False,
            "include_body": False,
            "mask_sensitive_data": True
        },
        "loggers": {
            "aws_services": {"level": "info"},
            "image_processing": {"level": "debug"},
            "langchain": {"level": "info"},
            "fastapi": {"level": "warning"}
        }
    }
    
    # If config file exists, load it
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            print(f"Error loading logging config: {e}. Using default configuration.")
            return default_config
    else:
        return default_config

def get_formatter(format_type):
    """
    Get formatter based on format type
    
    Args:
        format_type (str): Format type (standard, json, simple)
        
    Returns:
        logging.Formatter: Formatter instance
    """
    if format_type == "json":
        return JsonFormatter()
    elif format_type == "simple":
        return logging.Formatter(SIMPLE_LOG_FORMAT)
    else:  # standard
        return logging.Formatter(DEFAULT_LOG_FORMAT)

def setup_logging(config_override=None):
    """
    Set up logging configuration for the application
    
    Args:
        config_override (dict): Override default configuration
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Load configuration
    config = get_config()
    
    # Apply overrides if provided
    if config_override:
        # Deep merge the dictionaries
        def merge_dicts(d1, d2):
            for k, v in d2.items():
                if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                    merge_dicts(d1[k], v)
                else:
                    d1[k] = v
        
        merge_dicts(config, config_override)
    
    # Get app name and default log level
    app_name = config["general"]["app_name"]
    default_level = LOG_LEVELS.get(config["general"]["default_level"].lower(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(default_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler if enabled
    if config["console"]["enabled"]:
        console_level = LOG_LEVELS.get(config["console"]["level"].lower(), default_level)
        console_format = config["console"]["format"]
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(get_formatter(console_format))
        root_logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if config["file"]["enabled"]:
        file_level = LOG_LEVELS.get(config["file"]["level"].lower(), default_level)
        file_format = config["file"]["format"]
        
        # Create log directory
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / config["file"]["directory"]
        os.makedirs(log_dir, exist_ok=True)
        
        # Base log file path
        log_file = os.path.join(log_dir, f"{app_name}.log")
        
        # Check if rotation is enabled
        if config["file"]["rotation"]["enabled"]:
            rotation_config = config["file"]["rotation"]
            
            # Size-based rotation
            if "max_size_mb" in rotation_config:
                max_bytes = rotation_config["max_size_mb"] * 1024 * 1024
                backup_count = rotation_config.get("backup_count", 5)
                
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count
                )
            
            # Time-based rotation
            elif "when" in rotation_config:
                when = rotation_config["when"]
                interval = rotation_config.get("interval", 1)
                backup_count = rotation_config.get("backup_count", 5)
                
                file_handler = TimedRotatingFileHandler(
                    log_file,
                    when=when,
                    interval=interval,
                    backupCount=backup_count
                )
            
            else:
                # Fallback to standard file handler
                file_handler = logging.FileHandler(log_file)
        else:
            # No rotation
            file_handler = logging.FileHandler(log_file)
        
        # Set level and formatter
        file_handler.setLevel(file_level)
        file_handler.setFormatter(get_formatter(file_format))
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    if "loggers" in config:
        for logger_name, logger_config in config["loggers"].items():
            logger = logging.getLogger(logger_name)
            if "level" in logger_config:
                logger.setLevel(LOG_LEVELS.get(logger_config["level"].lower(), default_level))
    
    # Create application logger
    logger = logging.getLogger(app_name)
    logger.setLevel(default_level)
    
    return logger

def get_logger(name):
    """
    Get a logger with the given name
    
    Args:
        name (str): Name for the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter to add contextual information to log records
    """
    def process(self, msg, kwargs):
        # Add extra contextual info to the log record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Add request_id if provided
        if hasattr(self, 'request_id'):
            kwargs['extra']['request_id'] = self.request_id
            
        # Add user_id if provided
        if hasattr(self, 'user_id'):
            kwargs['extra']['user_id'] = self.user_id
            
        return msg, kwargs

def get_request_logger(name, request_id=None, user_id=None):
    """
    Get a logger with request context information
    
    Args:
        name (str): Name for the logger
        request_id (str): ID of the current request
        user_id (str): ID of the current user
        
    Returns:
        LoggerAdapter: Logger adapter with request context
    """
    logger = logging.getLogger(name)
    adapter = LoggerAdapter(logger, {})
    
    if request_id:
        adapter.request_id = request_id
    
    if user_id:
        adapter.user_id = user_id
        
    return adapter

class PerformanceLoggerAdapter(LoggerAdapter):
    """
    Logger adapter that includes performance metrics
    """
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
        self.start_times = {}
    
    def start_timer(self, operation_name):
        """Start timing an operation"""
        import time
        self.start_times[operation_name] = time.time()
    
    def stop_timer(self, operation_name, log_level="info", message=None):
        """Stop timing and log the duration"""
        import time
        if operation_name in self.start_times:
            duration_ms = (time.time() - self.start_times[operation_name]) * 1000
            
            # Create log message
            if message is None:
                message = f"Operation '{operation_name}' completed"
            else:
                message = f"{message} (operation: {operation_name})"
                
            # Add memory usage if configured
            memory_usage = None
            config = get_config()
            if config["metrics"]["include_memory"]:
                try:
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
                except ImportError:
                    pass
            
            # Prepare extra info
            extra = {'duration_ms': duration_ms}
            if memory_usage:
                extra['memory_usage'] = memory_usage
                
            # Log at the appropriate level
            log_method = getattr(self.logger, log_level.lower())
            log_method(f"{message} - Duration: {duration_ms:.2f}ms", extra=extra)
            
            # Clean up
            del self.start_times[operation_name]
        else:
            self.logger.warning(f"Timer for operation '{operation_name}' was never started")

def get_performance_logger(name):
    """
    Get a logger with performance monitoring capabilities
    
    Args:
        name (str): Name for the logger
        
    Returns:
        PerformanceLoggerAdapter: Logger adapter with performance monitoring
    """
    logger = logging.getLogger(name)
    return PerformanceLoggerAdapter(logger)
