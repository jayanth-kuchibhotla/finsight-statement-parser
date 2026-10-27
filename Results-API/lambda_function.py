import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

STATEMENTS_TABLE = os.environ.get("STATEMENTS_TABLE", "finsight-statements")
TRANSACTIONS_TABLE = os.environ.get("TRANSACTIONS_TABLE", "finsight-transactions")

class StatementProcessingError(Exception):
    """Custom exception for statement processing errors."""
    pass

def return_transactions(record):
    try:
        # Step 1: Receive GET request from API Gateway event
        try:
            path_params = record.get("pathParameters", {})
            statement_id = path_params.get("statement_id")
            
            logger.info(f"Processing GET request for statement ID: {statement_id}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Invalid GET request format: {e}")
            raise StatementProcessingError("Invalid GET request format")
        
        # Step 2: Get statement ID from statements table
        try:
            statement_response = dynamodb_client.get_item(
                TableName=STATEMENTS_TABLE,
                Key={"statement_id": {"S": statement_id}}
            )
            
            logger.info(f"Retrieved statement for ID {statement_id}: {statement_response}")
        except Exception as e:
            logger.error(f"Error querying DynamoDB for statement ID {statement_id}: {e}")
            raise StatementProcessingError("Error querying statement from DynamoDB")
        
        # Step 3: Query transactions table from statement ID for transactions
        if "Item" in statement_response:
            try:
                transactions_response = dynamodb_client.query(
                    TableName=TRANSACTIONS_TABLE,
                    IndexName="StatementIDIndex",
                    KeyConditionExpression="statement_id = :sid",
                    ExpressionAttributeValues={":sid": {"S": statement_id}}
                )
                
                logger.info(f"Retrieved transactions for statement ID {statement_id}: {transactions_response}")
            except Exception as e:
                logger.error(f"Error querying DynamoDB for transactions with statement ID {statement_id}: {e}")
                raise StatementProcessingError("Error querying transactions from DynamoDB")
        else:
            logger.warning(f"No statement found for ID {statement_id}")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Statement not found"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # Step 4: Deserialize transactions and return as Python dicts
        statement_item = statement_response["Item"]
        statement = {
            "statement_id": statement_item["statement_id"]["S"],
            "account_holder": statement_item["account_holder"]["S"],
            "account_number": statement_item["account_number"]["S"],
            "bank": statement_item["bank"]["S"],
            "statement_period_from": statement_item["statement_period_from"]["S"],
            "statement_period_to": statement_item["statement_period_to"]["S"],
            "total_credits": float(statement_item["total_credits"]["N"]),
            "total_debits": float(statement_item["total_debits"]["N"]),
            "transaction_count": int(statement_item["transaction_count"]["N"]),
            "processed_at": statement_item["processed_at"]["S"],
            "status": statement_item["status"]["S"]
        }
        
        transactions = []
        
        for item in transactions_response.get("Items", []):
            transaction = {
                "transaction_id": item["transaction_id"]["S"],
                "date": item["date"]["S"],
                "description": item["description"]["S"],
                "amount": float(item["amount"]["N"]),
                "type": item["type"]["S"],
                "balance": float(item["balance"]["N"]),
                "category": item["category"]["S"],
                "rank": int(item["rank"]["N"])
            }
            transactions.append(transaction)
            
        # Step 5: Return the transactions as a JSON response
        return {
            "statusCode": 200,
            "body": json.dumps({"statement": statement, "transactions": transactions}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        logger.error(f"Error processing statement ID {statement_id}: {type(e).__name__}: {e}")
        raise StatementProcessingError("Error processing statement ID")
    
def lambda_handler(event, context):
    try:
        return return_transactions(event)
    except StatementProcessingError:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
            "headers": {"Content-Type": "application/json"}
        }
