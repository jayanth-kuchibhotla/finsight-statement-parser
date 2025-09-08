import json
import logging
import os
import boto3
import tempfile
from botocore.exceptions import ClientError
from datetime import datetime

# Import parser functions
from Parser_Functions.parser_sbi import parser_sbi_fun
from Parser_Functions.parser_hdfc import parser_hdfc_fun
from Parser_Functions.parser_icici import parser_icici_fun
from Parser_Functions.parser_axis import parser_axis_fun
from Parser_Functions.parser_kotak import parser_kotak_fun

# Import other utilities
from decrypt_pdf import try_bank_passwords
from bank_identifier import identify_bank
from log_to_cloudwatch import log_to_cloudwatch

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 clients
s3_client = boto3.client("s3")

# Get environment variables
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

class StatementProcessingError(Exception):
    """Custom exception for statement processing errors."""
    pass

def process_message(record):
    """
    Processes a single SQS message, handling statement parsing.
    """
    message_id = record.get("messageId", "N/A")
    s3_key = None
    local_pdf_path = None
    decrypted_pdf_path = None

    try:
        # Step 1: Process SQS message
        try:
            message_body = json.loads(record["body"])
            s3_key = message_body["s3_key"]
            password = message_body.get("password")
            log_to_cloudwatch("INFO", f"Processing message {message_id} for S3 key: {s3_key}")
        except (json.JSONDecodeError, KeyError) as e:
            log_to_cloudwatch("ERROR", f"Invalid SQS message format for message ID {message_id}: {e}")
            raise StatementProcessingError("Invalid SQS message format")

        # Step 2: Download file from S3
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                local_pdf_path = temp_file.name
            s3_client.download_file(S3_BUCKET_NAME, s3_key, local_pdf_path)
            log_to_cloudwatch("INFO", f"Successfully downloaded {s3_key} from S3.")
        except ClientError as e:
            log_to_cloudwatch("ERROR", f"Failed to download {s3_key} from S3: {e}")
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise StatementProcessingError(f"S3 object not found: {s3_key}")
            raise StatementProcessingError("Failed to download from S3")

        # Step 3: Decrypt PDF if password is provided
        if password:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    decrypted_pdf_path = temp_file.name
                
                if not try_bank_passwords(local_pdf_path, password, decrypted_pdf_path):
                    raise StatementProcessingError("Decryption returned False. Check password or file integrity.")
                
                # Replace original path with decrypted path for subsequent steps
                os.remove(local_pdf_path)
                local_pdf_path = decrypted_pdf_path
                log_to_cloudwatch("INFO", f"PDF decrypted successfully for {s3_key}.")
            except Exception as e:
                log_to_cloudwatch("ERROR", f"Decryption failed for {s3_key}: {e}")
                raise StatementProcessingError("Decryption failed")

        # Step 4: Identify bank
        try:
            bank = identify_bank(local_pdf_path)
            if bank == "unknown":
                raise StatementProcessingError("Could not identify the bank from the statement.")
            log_to_cloudwatch("INFO", f"Identified bank for {s3_key}: {bank}")
        except Exception as e:
            log_to_cloudwatch("ERROR", f"Bank identification failed for {s3_key}: {e}")
            raise StatementProcessingError("Bank identification failed")

        # Step 5: Parse statement
        statement_data, transactions = {}, []
        parsers = {
            "sbi": parser_sbi_fun, "hdfc": parser_hdfc_fun, "icici": parser_icici_fun,
            "axis": parser_axis_fun, "kotak": parser_kotak_fun,
        }
        parser_function = parsers.get(bank)
        if parser_function:
            try:
                _, statement_data, transactions = parser_function(local_pdf_path)
                log_to_cloudwatch("INFO", f"Parsed statement for {s3_key}, account: {statement_data.get('account_number')}")
                status = "PROCESSED"
            except Exception as e:
                log_to_cloudwatch("ERROR", f"Parser failed for {bank} on {s3_key}: {e}")
                statement_data = {"error": str(e)}
                transactions = []
                status = "FAILED"
        else:
            log_to_cloudwatch("WARNING", f"No parser available for bank: {bank}")
            statement_data = {"error": f"No parser available for {bank}"}
            transactions = []
            status = "FAILED"

        # Step 6: Store parsed data in S3
        try:
            parsed_key = s3_key.replace("uploads/", "parsed/").replace(".pdf", ".json")
            s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=parsed_key,
            Body=json.dumps({"bank": bank, "status": status, "statement": statement_data, "transactions": transactions, "processed_at": datetime.utcnow().isoformat()}),
            )
            log_to_cloudwatch("INFO", f"Stored parsed result in S3 at {parsed_key}")
        except ClientError as e:
            log_to_cloudwatch("ERROR", f"Failed to store parsed data in S3 for {parsed_key}: {e}")
            raise StatementProcessingError("Failed to store data in S3")

    finally:
        # Clean up temporary files
        if local_pdf_path and os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)
        # This check prevents trying to delete the same file twice if decryption happened in-place
        if decrypted_pdf_path and os.path.exists(decrypted_pdf_path) and local_pdf_path != decrypted_pdf_path:
            os.remove(decrypted_pdf_path)

def lambda_handler(event, context):
    failed_messages = []
    for record in event.get("Records", []):
        try:
            process_message(record)
        except StatementProcessingError as e:
            message_id = record.get("messageId", "N/A")
            log_to_cloudwatch("ERROR", f"Critical failure in processing message ID {message_id}: {e}")
            failed_messages.append({"itemIdentifier": message_id})
            
    return {"batchItemFailures": failed_messages}
