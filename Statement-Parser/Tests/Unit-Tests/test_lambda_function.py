import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

os.environ['S3_BUCKET_NAME'] = 'test-bucket'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['BEDROCK_QUEUE_URL'] = 'test-queue-url'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from lambda_function import lambda_handler, StatementProcessingError, process_message


class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.sqs_client')
    @patch('lambda_function.s3_client')
    @patch('lambda_function.identify_bank')
    @patch('lambda_function.pikepdf')
    @patch('lambda_function.parser_sbi_fun')
    @patch('lambda_function.log_to_cloudwatch')
    def test_lambda_handler_success(self, mock_log, mock_parser, mock_pikepdf, mock_identify, mock_s3, mock_sqs):
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

        mock_identify.return_value = 'sbi'
        mock_parser.return_value = ('', {"account_number": "12345"}, [], "raw text")
        mock_s3.download_file = MagicMock()
        mock_pikepdf.open.return_value.__enter__ = MagicMock()
        mock_pikepdf.PasswordError = Exception

        result = lambda_handler(event, {})

        self.assertEqual(result, {"batchItemFailures": []})
        mock_s3.download_file.assert_called_once()
        mock_identify.assert_called_once()
        mock_parser.assert_called_once()
        mock_sqs.send_message.assert_called_once()

    @patch('lambda_function.log_to_cloudwatch')
    def test_lambda_handler_invalid_message(self, mock_log):
        event = {
            "Records": [
                {
                    "messageId": "456",
                    "body": "invalid-json"
                }
            ]
        }

        result = lambda_handler(event, {})

        self.assertEqual(len(result['batchItemFailures']), 1)
        self.assertEqual(result['batchItemFailures'][0]['itemIdentifier'], '456')

    @patch('lambda_function.log_to_cloudwatch')
    @patch('lambda_function.identify_bank', return_value="unknown")
    @patch('lambda_function.s3_client')
    def test_process_message_unknown_bank(self, mock_s3, mock_identify, mock_log):
        record = {"messageId": "789", "body": json.dumps({"s3_key": "uploads/test.pdf"})}
        mock_s3.download_file = MagicMock()

        with self.assertRaises(StatementProcessingError):
            process_message(record)

    @patch('lambda_function.log_to_cloudwatch')
    @patch('lambda_function.s3_client')
    def test_process_message_s3_download_failure(self, mock_s3, mock_log):
        record = {"messageId": "999", "body": json.dumps({"s3_key": "uploads/missing.pdf"})}

        error_response = {"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}
        mock_s3.download_file.side_effect = ClientError(error_response, "DownloadFile")

        with self.assertRaises(StatementProcessingError):
            process_message(record)


if __name__ == '__main__':
    unittest.main()