import sys
import os
from unittest.mock import MagicMock, patch
import unittest

# Mock the ewalambdacore module before importing the lambda_function
sys.modules['ewalambdacore'] = MagicMock()
sys.modules['ewalambdacore.httpwrapper'] = MagicMock()

# Add the parent directory to the system path to allow for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lambda_function import lambda_handler

class TestPresignedUrlLambda(unittest.TestCase):

    @patch('boto3.client')
    def test_lambda_handler_success(self, mock_boto_client):
        # Mock API Gateway event
        event = {
            "queryStringParameters": {
                "bucket": "fintech-statement-parser-bucket",
                "filepath": "uploads/test.pdf"
            }
        }

        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_post.return_value = {"url": "http://example.com", "fields": {}}

        # Call the handler
        result = lambda_handler(event, {})

        # Assertions
        self.assertEqual(result, {"url": "http://example.com", "fields": {}})
        mock_s3.generate_presigned_post.assert_called_once()

    def test_lambda_handler_missing_bucket(self):
        # Mock API Gateway event
        event = {
            "queryStringParameters": {
                "filepath": "uploads/test.pdf"
            }
        }

        # Call the handler
        lambda_handler(event, {})

    def test_lambda_handler_missing_filepath(self):
        # Mock API Gateway event
        event = {
            "queryStringParameters": {
                "bucket": "fintech-statement-parser-bucket"
            }
        }

        # Call the handler
        lambda_handler(event, {})

    def test_lambda_handler_invalid_bucket(self):
        # Mock API Gateway event
        event = {
            "queryStringParameters": {
                "bucket": "invalid-bucket",
                "filepath": "uploads/test.pdf"
            }
        }

        # Call the handler
        lambda_handler(event, {})

if __name__ == '__main__':
    unittest.main()
