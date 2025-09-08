import time
import json
import boto3
import os

cloudwatch = boto3.client("logs")
LOG_GROUP = os.environ.get("LOG_GROUP_NAME", "statement-service-logs")

def log_to_cloudwatch(message: dict, pages_count: int = None, duration: float = None):
    """
    Logs parsing process results to AWS CloudWatch.
    """
    log_stream = f"statement-parser-{message.get('statement_id', 'unknown')}"
    
    # Ensure log stream exists
    try:
        cloudwatch.create_log_stream(logGroupName=LOG_GROUP, logStreamName=log_stream)
    except cloudwatch.exceptions.ResourceAlreadyExistsException:
        pass
    
    # Base log event
    timestamp = int(round(time.time() * 1000))
    
    if message.get("verdict") == "failure":
        log_event = {
            "description": "Error Occurred",
            "level": "ERROR",
            **message,
            "pages_count": pages_count,
            "total_duration": duration,
        }
    else:
        log_event = {
            "description": "Process Finished Successfully",
            "level": "INFO",
            **message,
            "pages_count": pages_count,
            "total_duration": duration,
        }
    
    # Get sequence token if required
    kwargs = {
        "logGroupName": LOG_GROUP,
        "logStreamName": log_stream,
        "logEvents": [
            {
                "timestamp": timestamp,
                "message": json.dumps(log_event),
            }
        ],
    }
    try:
        response = cloudwatch.put_log_events(**kwargs)
    except cloudwatch.exceptions.InvalidSequenceTokenException as e:
        token = e.response["expectedSequenceToken"]
        kwargs["sequenceToken"] = token
        response = cloudwatch.put_log_events(**kwargs)

    return response
