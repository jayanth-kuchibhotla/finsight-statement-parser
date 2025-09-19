import unittest
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import logging

logging.disable(logging.CRITICAL)

# Set environment variables for testing
os.environ['INPUT_QUEUE_URL'] = 'test-queue-url'

# Add the parent directory to the system path to allow for import
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from lambda_function import lambda_handler


class TestS3TriggerLambda(unittest.TestCase):

    @patch('lambda_function.sqs_client')
    @patch('lambda_function.s3_client')
    def test_lambda_handler_success(self, mock_s3_client, mock_sqs_client):
        # Mock S3 event
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "uploads/test.pdf"}
                    }
                }
            ]
        }

        # Mock S3 head_object to return metadata
        mock_s3_client.head_object.return_value = {
            "Metadata": {"password": "test_password"}
        }

        # Mock SQS send_message
        mock_sqs_client.send_message.return_value = {}

        # Call the handler
        result = lambda_handler(event, {})

        # Assertions
        self.assertEqual(result, {"statusCode": 200, "body": "S3 records processed successfully."})
        mock_s3_client.head_object.assert_called_once_with(Bucket='test-bucket', Key='uploads/test.pdf')
        mock_sqs_client.send_message.assert_called_once()

    @patch('lambda_function.sqs_client')
    @patch('lambda_function.s3_client')
    def test_lambda_handler_s3_error(self, mock_s3_client, mock_sqs_client):
        # Simulate S3 throwing a ClientError
        mock_s3_client.head_object.side_effect = ClientError(
            {'Error': {'Code': '403', 'Message': 'Forbidden'}}, 'HeadObject'
        )

        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "uploads/test.pdf"}
                    }
                }
            ]
        }

        result = lambda_handler(event, {})

        # Assertions
        self.assertEqual(len(result['batchItemFailures']), 1)
        self.assertEqual(result['batchItemFailures'][0]['itemIdentifier'], 'uploads/test.pdf')


if __name__ == '__main__':
    unittest.main()
