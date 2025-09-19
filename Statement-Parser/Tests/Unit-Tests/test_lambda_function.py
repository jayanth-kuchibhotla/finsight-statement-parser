import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Set environment variables for testing
os.environ['S3_BUCKET_NAME'] = 'test-bucket'
os.environ['LOG_LEVEL'] = 'INFO'

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lambda_function import lambda_handler, StatementProcessingError, process_message


class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.s3_client')
    @patch('lambda_function.identify_bank')
    @patch('lambda_function.try_bank_passwords')
    @patch('lambda_function.parser_sbi_fun')
    @patch('lambda_function.log_to_cloudwatch')
    @patch('lambda_function.datetime')
    def test_lambda_handler_success(self, mock_datetime, mock_log, mock_parser, mock_decrypt, mock_identify, mock_s3):
        # Mock SQS event
        event = {
            "Records": [
                {
                    "messageId": "123",
                    "body": json.dumps({
                        "s3_key": "uploads/test.pdf",
                        "password": "test_password"
                    })
                }
            ]
        }

        # Mock functions
        mock_identify.return_value = 'sbi'
        mock_decrypt.return_value = True
        mock_parser.return_value = ('', {"account_number": "12345"}, [])
        mock_s3.download_file = MagicMock()
        mock_s3.put_object = MagicMock()
        mock_datetime.datetime.now.return_value = "2025-01-01T00:00:00Z"

        # Call the handler
        result = lambda_handler(event, {})

        # Assertions
        self.assertEqual(result, {"batchItemFailures": []})
        mock_s3.download_file.assert_called_once()
        mock_s3.put_object.assert_called_once()
        mock_identify.assert_called_once()
        mock_decrypt.assert_called_once()
        mock_parser.assert_called_once()

    @patch('lambda_function.log_to_cloudwatch')
    def test_lambda_handler_invalid_message(self, mock_log):
        # Mock SQS event with invalid JSON
        event = {
            "Records": [
                {
                    "messageId": "456",
                    "body": "invalid-json"
                }
            ]
        }

        # Call the handler
        result = lambda_handler(event, {})

        # Assertions
        self.assertEqual(len(result['batchItemFailures']), 1)
        self.assertEqual(result['batchItemFailures'][0]['itemIdentifier'], '456')
        mock_log.assert_any_call("ERROR", unittest.mock.ANY)

    @patch('lambda_function.s3_client')
    @patch('lambda_function.identify_bank', return_value="unknown")
    @patch('lambda_function.log_to_cloudwatch')
    def test_process_message_unknown_bank(self, mock_log, mock_identify, mock_s3):
        record = {"messageId": "789", "body": json.dumps({"s3_key": "uploads/test.pdf"})}
        mock_s3.download_file = MagicMock()

        with self.assertRaises(StatementProcessingError):
            process_message(record)

        mock_log.assert_any_call("ERROR", unittest.mock.ANY)

    @patch('lambda_function.s3_client')
    @patch('lambda_function.log_to_cloudwatch')
    def test_process_message_s3_download_failure(self, mock_log, mock_s3):
        record = {"messageId": "999", "body": json.dumps({"s3_key": "uploads/missing.pdf"})}
        
        # Simulate S3 throwing a NoSuchKey error
        error_response = {"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}
        mock_s3.download_file.side_effect = ClientError(error_response, "DownloadFile")

        with self.assertRaises(StatementProcessingError):
            process_message(record)

        mock_log.assert_any_call("ERROR", unittest.mock.ANY)


if __name__ == '__main__':
    unittest.main()
