import json
import logging
import os
import boto3
import urllib.parse
from botocore.exceptions import ClientError

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3_client = boto3.client("s3")
sqs_client = boto3.client("sqs")

# Get environment variables
INPUT_QUEUE_URL = os.environ.get("INPUT_QUEUE_URL")

def lambda_handler(event, context):
    """
    Triggered by an S3 event, sends a message to an SQS queue.
    """
    failures = []  # Track failed records

    for record in event.get("Records", []):
        try:
            s3_bucket = record["s3"]["bucket"]["name"]
            s3_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

            # Get the password from the S3 object metadata (if available)
            head_object = s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
            password = head_object.get("Metadata", {}).get("password")

            if not password:
                logger.warning(f"No password metadata found for {s3_key}")

            # Construct the message
            message = {
                "s3_bucket": s3_bucket,
                "s3_key": s3_key,
                "password": password
            }

            # Send the message to the input queue
            sqs_client.send_message(
                QueueUrl=INPUT_QUEUE_URL,
                MessageBody=json.dumps(message)
            )
            logger.info(f"Sent message to SQS for S3 key: {s3_key}")

        except Exception as e:
            logger.exception(f"Error processing S3 event record for {record}: {e}")
            failures.append({"itemIdentifier": s3_key})

    # If any records failed, tell Lambda to retry them / send to DLQ
    if failures:
        return {"batchItemFailures": failures}

    return {"statusCode": 200, "body": "S3 records processed successfully."}
