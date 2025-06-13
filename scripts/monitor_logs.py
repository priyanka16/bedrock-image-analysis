#!/usr/bin/env python
"""
Log monitoring script for the image analysis application

This script reads and analyzes log files, providing summaries,
error reporting, and performance metrics.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import statistics

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Monitor and analyze log files")
    parser.add_argument("--log-dir", 
                        default=os.path.join(Path(__file__).parent, "logs"),
                        help="Directory containing log files")
    parser.add_argument("--hours", type=int, default=24,
                        help="Hours of logs to analyze")
    parser.add_argument("--min-level", default="warning",
                        choices=["debug", "info", "warning", "error", "critical"],
                        help="Minimum log level to include in report")
    parser.add_argument("--json", action="store_true",
                        help="Output report as JSON")
    parser.add_argument("--metrics", action="store_true",
                        help="Include performance metrics in report")
    parser.add_argument("--alerts", action="store_true",
                        help="Check for alertable conditions")
    parser.add_argument("--alert-threshold", type=int, default=5,
                        help="Number of errors before alerting")
    return parser.parse_args()

def get_log_files(log_dir, hours=24):
    """Get log files modified in the past N hours"""
    files = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for file in Path(log_dir).glob("*.log*"):
        # Check file modification time
        if file.stat().st_mtime >= cutoff_time.timestamp():
            files.append(str(file))
    
    return files

def parse_log_line(line):
    """Parse a log line into a structured object"""
    try:
        # Try parsing as JSON first
        return json.loads(line)
    except json.JSONDecodeError:
        # Fall back to regex parsing
        log_pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (?P<name>[\w\.]+) - (?P<level>\w+) - \[(?P<file>[\w\.]+):(?P<line>\d+)\] - (?P<message>.*)'
        match = re.match(log_pattern, line)
        if match:
            return match.groupdict()
        return None

def get_log_level_value(level):
    """Convert log level string to numeric value"""
    levels = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40,
        "critical": 50
    }
    return levels.get(level.lower(), 0)

def analyze_logs(log_files, min_level="warning", include_metrics=False):
    """Analyze log files and generate report"""
    results = {
        "total_logs": 0,
        "logs_by_level": defaultdict(int),
        "errors": [],
        "requests": defaultdict(int),
        "slowest_operations": []
    }
    
    performance_data = defaultdict(list)
    min_level_value = get_log_level_value(min_level)
    
    for log_file in log_files:
        try:
            with open(log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    log_entry = parse_log_line(line)
                    if not log_entry:
                        continue
                    
                    results["total_logs"] += 1
                    
                    # Get log level
                    level = log_entry.get("level", "").lower()
                    results["logs_by_level"][level] += 1
                    
                    # Check if we should include this level
                    level_value = get_log_level_value(level)
                    if level_value < min_level_value:
                        continue
                    
                    # Track request IDs
                    if "request_id" in log_entry:
                        results["requests"][log_entry["request_id"]] += 1
                    
                    # Track errors
                    if level_value >= 40:  # Error or critical
                        error_entry = {
                            "timestamp": log_entry.get("timestamp"),
                            "message": log_entry.get("message"),
                            "file": log_entry.get("file"),
                            "line": log_entry.get("line")
                        }
                        if "exception" in log_entry:
                            error_entry["exception"] = log_entry["exception"]
                        results["errors"].append(error_entry)
                    
                    # Track performance metrics
                    if include_metrics and "duration_ms" in log_entry:
                        operation = log_entry.get("message", "").split(" (operation: ")[-1].split(")")[0]
                        if operation:
                            performance_data[operation].append(float(log_entry["duration_ms"]))
        except Exception as e:
            print(f"Error processing log file {log_file}: {e}", file=sys.stderr)
    
    # Process performance data
    if include_metrics and performance_data:
        for operation, durations in performance_data.items():
            if len(durations) > 1:
                results["slowest_operations"].append({
                    "operation": operation,
                    "avg_duration_ms": round(statistics.mean(durations), 2),
                    "max_duration_ms": round(max(durations), 2),
                    "min_duration_ms": round(min(durations), 2),
                    "count": len(durations)
                })
        
        # Sort by average duration (slowest first)
        results["slowest_operations"].sort(key=lambda x: x["avg_duration_ms"], reverse=True)
    
    return results

def format_text_report(results):
    """Format results as text report"""
    report = []
    
    report.append("=== Log Analysis Report ===")
    report.append(f"Total logs: {results['total_logs']}")
    report.append("\nLog levels:")
    for level, count in sorted(results["logs_by_level"].items(), 
                              key=lambda x: get_log_level_value(x[0])):
        report.append(f"  {level.upper()}: {count}")
    
    report.append(f"\nTotal requests: {len(results['requests'])}")
    
    report.append(f"\nErrors: {len(results['errors'])}")
    for i, error in enumerate(results["errors"][:10], 1):
        report.append(f"\n{i}. {error.get('timestamp', 'N/A')} - {error.get('file', 'N/A')}:{error.get('line', 'N/A')}")
        report.append(f"   {error.get('message', 'N/A')}")
        if "exception" in error:
            exception_lines = error["exception"].split("\n")
            report.append(f"   {exception_lines[0]}")
    
    if len(results["errors"]) > 10:
        report.append(f"\n... and {len(results['errors']) - 10} more errors")
    
    if results["slowest_operations"]:
        report.append("\nSlowest operations:")
        for i, op in enumerate(results["slowest_operations"][:5], 1):
            report.append(f"{i}. {op['operation']}")
            report.append(f"   Avg: {op['avg_duration_ms']}ms, Max: {op['max_duration_ms']}ms, Count: {op['count']}")
    
    return "\n".join(report)

def check_for_alerts(results, threshold=5):
    """Check if any alert conditions are met"""
    alerts = []
    
    # Check for number of errors
    error_count = len(results["errors"])
    if error_count >= threshold:
        alerts.append(f"ALERT: {error_count} errors detected (threshold: {threshold})")
    
    # Check for slow operations
    for op in results["slowest_operations"]:
        if op["avg_duration_ms"] > 1000:  # Over 1 second
            alerts.append(f"ALERT: Slow operation detected: {op['operation']} ({op['avg_duration_ms']}ms)")
    
    return alerts

def main():
    """Main function"""
    args = parse_args()
    
    # Get log files
    log_files = get_log_files(args.log_dir, args.hours)
    if not log_files:
        print(f"No log files found in {args.log_dir} from the past {args.hours} hours")
        return 1
    
    # Analyze logs
    results = analyze_logs(log_files, args.min_level, args.metrics)
    
    # Output report
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text_report(results))
    
    # Check for alerts
    if args.alerts:
        alerts = check_for_alerts(results, args.alert_threshold)
        if alerts:
            print("\n" + "\n".join(alerts))
            return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
