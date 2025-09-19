import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Parser_Functions')))


from parser_axis import parser_axis_fun

class TestParserAxis(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_parser_axis_fun(self, mock_pdfplumber_open):
        # Mock the PDF content
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
            Account No : 912345678901
            Name : John Doe
            Statement of account for the period of : 01-Jan-2023 to 31-Jan-2023
            Branch : MUMBAI
            Date Chq No Description Debit Credit Balance
            02-Jan-23 123456 SALARY 0.00 50,000.00 50,000.00
            05-Jan-23 654321 RENT 10,000.00 0.00 40,000.00
        """
        mock_pdf.pages = [mock_page1]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        status, statement_info, transactions = parser_axis_fun('dummy.pdf')

        # Assertions
        self.assertEqual(status, "without_timestamps")
        
        # Statement info assertions
        self.assertEqual(statement_info['bank_code'], 'axis')
        self.assertEqual(statement_info['account_number'], '912345678901')
        self.assertEqual(statement_info['user_name'], 'John Doe')
        self.assertEqual(statement_info['statement_start'], '2023-01-01')
        self.assertEqual(statement_info['statement_end'], '2023-01-31')
        self.assertEqual(statement_info['bank_branch'], 'MUMBAI')

        # Transactions assertions
        self.assertEqual(len(transactions), 2)
        
        # First transaction
        self.assertEqual(transactions[0]['date'], '2023-01-02')
        self.assertEqual(transactions[0]['description'], 'SALARY')
        self.assertEqual(transactions[0]['amount'], 50000.00)
        self.assertEqual(transactions[0]['balance'], 50000.00)
        self.assertEqual(transactions[0]['transaction_type'], 'credit')

        # Second transaction
        self.assertEqual(transactions[1]['date'], '2023-01-05')
        self.assertEqual(transactions[1]['description'], 'RENT')
        self.assertEqual(transactions[1]['amount'], -10000.00)
        self.assertEqual(transactions[1]['balance'], 40000.00)
        self.assertEqual(transactions[1]['transaction_type'], 'debit')

if __name__ == '__main__':
    unittest.main()
