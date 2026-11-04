import json
import logging
import os
import boto3

from uuid import uuid4

from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")
bedrock_client = boto3.client("bedrock-runtime")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

STATEMENTS_TABLE = os.environ.get("STATEMENTS_TABLE", "finsight-statements")
TRANSACTIONS_TABLE = os.environ.get("TRANSACTIONS_TABLE", "finsight-transactions")

class StatementProcessingError(Exception):
    """Custom exception for statement processing errors."""
    pass

def categorize_statement(record):

    message_id = record.get("messageId", "N/A")
    s3_key = None

    try:
        # Step 1: Process SQS message
        try:
            message = json.loads(record["body"])
            s3_key = message["s3_key"]
            statement_data = message["statement_data"]
            extracted_text = message["extracted_text"]

            logger.info(f"Processing message {message_id} for S3 key: {s3_key}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Invalid SQS message format for message ID {message_id}: {e}")
            raise StatementProcessingError("Invalid SQS message format")

        # Step 2: Construct prompt
        JSON_TEMPLATE = {
            "account_holder": "",
            "account_number": "",
            "bank": "",
            "statement_period": {"from": "", "to": ""},
            "transactions": [
                {
                "date": "YYYY-MM-DD",
                "description": "",
                "amount": 0.00,
                "type": "credit|debit",
                "balance": 0.00,
                "category": "",
                "rank": 0
                }
            ],
            "summary": {
                "total_credits": 0.00,
                "total_debits": 0.00,
                "transaction_count": 0
            }
        }

        prompt_content = f"""
        You are a financial data extraction assistant. Extract all transactions 
        from the following Indian bank statement text and return ONLY valid JSON, 
        no explanation, no markdown.

        Return this exact structure:
        {JSON_TEMPLATE}

        Categories must be one of: Food, Transport, Utilities, Shopping, 
        Entertainment, Healthcare, Education, Salary, Transfer, EMI, Tax, Other
        
        Rank each transaction by its original order in the statement, starting at 1.
        Preserve the original transaction order from the statement.

        Bank statement text:
        "{extracted_text}"
        """
        
        # Step 3: Call Bedrock
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt_content}]
        }

        response = bedrock_client.invoke_model(
            modelId = "anthropic.claude-haiku-20240307-v1:0",
            body = json.dumps(payload)
        )

        response_body = json.loads(response["body"].read().decode("utf-8"))
        extracted_data = (response_body["content"][0]["text"]).strip().removeprefix("```json").removesuffix("```").strip()
        parsed_data = json.loads(extracted_data)

        # Step 4: Write parsed data to DynamoDB
        ttl_value = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())

        statement_id = str(uuid4())

        dynamodb_client.put_item(
            TableName=STATEMENTS_TABLE,
            Item={
                "statement_id": {"S": statement_id},
                "account_holder": {"S": parsed_data["account_holder"]},
                "account_number": {"S": parsed_data["account_number"]},
                "bank": {"S": parsed_data["bank"]},
                "statement_period_from": {"S": parsed_data["statement_period"]["from"]},
                "statement_period_to": {"S": parsed_data["statement_period"]["to"]},
                "total_credits": {"N": str(parsed_data["summary"]["total_credits"])},
                "total_debits": {"N": str(parsed_data["summary"]["total_debits"])},
                "transaction_count": {"N": str(parsed_data["summary"]["transaction_count"])},
                "processed_at": {"S": datetime.now(timezone.utc).isoformat()},
                "s3_key": {"S": s3_key},
                "status": {"S": "PROCESSED"},
                "expires_at": {"N": str(ttl_value)}
            }
        )

        transactions = parsed_data["transactions"]
        chunks = [transactions[i:i+25] for i in range(0, len(transactions), 25)]

        for chunk in chunks:
            dynamodb_client.batch_write_item(
                RequestItems={
                    TRANSACTIONS_TABLE: [
                        {
                            "PutRequest": {
                                "Item": {
                                    "transaction_id": {"S": str(uuid4())},
                                    "statement_id": {"S": statement_id},
                                    "date": {"S": transaction["date"]},
                                    "description": {"S": transaction["description"]},
                                    "amount": {"N": str(transaction["amount"])},
                                    "type": {"S": transaction["type"]},
                                    "balance": {"N": str(transaction["balance"])},
                                    "category": {"S": transaction["category"]},
                                    "rank": {"N": str(transaction["rank"])},
                                    "expires_at": {"N": str(ttl_value)}
                                }
                            }
                        }
                        for transaction in chunk
                    ]
                }
            )
        
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {type(e).__name__}: {e}")
        raise StatementProcessingError("Error processing message")

def lambda_handler(event, context):
    failed_messages = []
    for record in event.get("Records", []):
        try:
            categorize_statement(record)
        except StatementProcessingError as e:
            message_id = record.get("messageId", "N/A")
            logger.error(f"Critical failure in processing message ID {message_id}: {e}")
            failed_messages.append({"itemIdentifier": message_id})
            
    return {"batchItemFailures": failed_messages}
