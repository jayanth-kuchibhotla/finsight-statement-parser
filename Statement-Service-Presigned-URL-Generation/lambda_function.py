import json
import boto3
from botocore.exceptions import ClientError

whitelisted_buckets = ["finsight-statement-parser-bucket"]

def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    print(event)

    params = event.get("queryStringParameters", {})

    if "bucket" not in params:
        return build_response(400, {"message": "bucket name is missing"})

    if "filepath" not in params:
        return build_response(400, {"message": "filepath is missing"})

    bucket_name = params["bucket"]
    filepath = params["filepath"]

    if bucket_name not in whitelisted_buckets:
        return build_response(400, {"message": "operation not allowed for bucket {0}".format(bucket_name)})

    s3_client = boto3.client("s3")

    try:
        conditions = [
            ["starts-with", "$x-amz-meta-statementRequestId", ""],
            ["starts-with", "$x-amz-meta-attachmentId", ""],
            ["starts-with", "$x-amz-meta-filename", ""],
        ]
        response = s3_client.generate_presigned_post(
            bucket_name, filepath, Conditions=conditions, ExpiresIn=300
        )
        print(response)

    except ClientError as exc:
        print(exc)
        print(type(exc))
        return None

    return build_response(200, response)
