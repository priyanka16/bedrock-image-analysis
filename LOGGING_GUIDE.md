# Logging System Guide

This document describes the logging system implemented in the Image Analysis application.

## Overview

The application includes a comprehensive logging system that provides:

- Structured logging with JSON output
- Log file rotation
- Performance metrics tracking
- Request tracking with request IDs
- Customizable log levels
- Log monitoring and analysis

## Configuration

Logging is configured through a YAML file located at `config/logging_config.yaml`. This allows you to customize logging behavior without code changes.

### Configuration Options

```yaml
# General configuration
general:
  app_name: image_analysis        # Application name
  default_level: info             # Default log level

# Console logging configuration
console:
  enabled: true                   # Enable console logs
  level: info                     # Console log level
  format: standard                # Log format (standard, json, simple)

# File logging configuration
file:
  enabled: true                   # Enable file logging
  level: debug                    # File log level
  format: json                    # Log format (standard, json, simple)
  directory: logs                 # Log directory
  # Rotation settings
  rotation:
    enabled: true                 # Enable log rotation
    max_size_mb: 10               # Max file size before rotation
    backup_count: 5               # Number of backup files to keep
    when: midnight                # When to rotate (S, M, H, D, midnight)
    interval: 1                   # Interval for rotation
```

## Using Loggers in Code

### Basic Usage

```python
from utils.logger_config import get_logger

# Create a logger
logger = get_logger("my_module")

# Log at different levels
logger.debug("Debug message with detailed information")
logger.info("Normal operation information")
logger.warning("Warning about potential issues")
logger.error("Error information", exc_info=True)  # Include exception info
```

### Request Tracking

```python
from utils.logger_config import get_request_logger

# Create a logger with request ID
logger = get_request_logger("api", request_id="123456", user_id="user123")

logger.info("Processing request")  # Will include request_id and user_id
```

### Performance Monitoring

```python
from utils.logger_config import get_performance_logger

# Create a performance logger
logger = get_performance_logger("image_processing")

# Time an operation
logger.start_timer("resize_image")
# ... perform image resize ...
logger.stop_timer("resize_image", message="Image resized successfully")
```

## Log Monitoring

The application includes a log monitoring script at `scripts/monitor_logs.py` that can analyze log files and generate reports.

### Basic Usage

```bash
# Analyze logs from the past 24 hours
python scripts/monitor_logs.py

# Analyze logs from the past 2 hours with JSON output
python scripts/monitor_logs.py --hours 2 --json

# Generate a report with only errors and critical logs
python scripts/monitor_logs.py --min-level error

# Include performance metrics in the report
python scripts/monitor_logs.py --metrics

# Check for alertable conditions
python scripts/monitor_logs.py --alerts --alert-threshold 3
```

### Example Output

```
=== Log Analysis Report ===
Total logs: 1245

Log levels:
  DEBUG: 753
  INFO: 421
  WARNING: 62
  ERROR: 9
  CRITICAL: 0

Total requests: 83

Errors: 9
1. 2023-06-15 14:23:45,123 - src/services/image_analysis.py:45
   Failed to analyze image: Invalid image format
   BotoServerError: 400 Bad Request

... and 4 more errors

Slowest operations:
1. analyze_image
   Avg: 2354.12ms, Max: 3521.45ms, Count: 83
2. resize_image
   Avg: 124.67ms, Max: 354.23ms, Count: 83
```

## Log File Rotation

The logging system automatically rotates log files based on size or time to prevent log files from growing too large. Rotated files are named with a suffix (e.g., `image_analysis.log.1`, `image_analysis.log.2`).

Two rotation strategies are available:

1. **Size-based rotation**: Rotates when a log file reaches a specified size
2. **Time-based rotation**: Rotates at specified time intervals

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened
   - ERROR: An error occurred but execution can continue
   - CRITICAL: A critical error that prevents execution

2. **Include contextual information**:
   - Always include request IDs for API calls
   - Include operation names for performance logging
   - Add user IDs when available

3. **Log structured data**:
   - Use JSON format for machine-readable logs
   - Include relevant metrics and operation details

4. **Monitor performance**:
   - Use performance loggers for critical operations
   - Set thresholds for alerts on slow operations

5. **Regular log analysis**:
   - Run the monitoring script regularly
   - Set up alerts for error thresholds
