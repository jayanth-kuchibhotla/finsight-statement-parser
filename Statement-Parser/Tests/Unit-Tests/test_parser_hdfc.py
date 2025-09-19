import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Parser_Functions')))

from parser_hdfc import parser_hdfc_fun

class TestParserHdfc(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_parser_hdfc_fun(self, mock_pdfplumber_open):
        # Mock the PDF content
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
            Account No : 123456789012
            Name : Jane Doe
            Statement From : 01/02/2023 To 28/02/2023
            Branch : DELHI
            Date Narration Ref No. Value Dt Withdrawal Amt. Deposit Amt. Balance
            03/02/23 SALARY 12345 03/02/23 0.00 60,000.00 60,000.00
            06/02/23 GROCERIES 54321 06/02/23 5,000.00 0.00 55,000.00
        """
        mock_pdf.pages = [mock_page1]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        status, statement_info, transactions = parser_hdfc_fun('dummy.pdf')

        # Assertions
        self.assertEqual(status, "without_timestamps")
        
        # Statement info assertions
        self.assertEqual(statement_info['bank_code'], 'hdfc')
        self.assertEqual(statement_info['account_number'], '123456789012')
        self.assertEqual(statement_info['user_name'], 'Jane Doe')
        self.assertEqual(statement_info['statement_start'], '2023-02-01')
        self.assertEqual(statement_info['statement_end'], '2023-02-28')
        self.assertEqual(statement_info['bank_branch'], 'DELHI')

        # Transactions assertions
        self.assertEqual(len(transactions), 2)
        
        # First transaction
        self.assertEqual(transactions[0]['date'], '2023-02-03')
        self.assertEqual(transactions[0]['description'], 'SALARY')
        self.assertEqual(transactions[0]['amount'], 60000.00)
        self.assertEqual(transactions[0]['balance'], 60000.00)
        self.assertEqual(transactions[0]['transaction_type'], 'credit')

        # Second transaction
        self.assertEqual(transactions[1]['date'], '2023-02-06')
        self.assertEqual(transactions[1]['description'], 'GROCERIES')
        self.assertEqual(transactions[1]['amount'], -5000.00)
        self.assertEqual(transactions[1]['balance'], 55000.00)
        self.assertEqual(transactions[1]['transaction_type'], 'debit')

if __name__ == '__main__':
    unittest.main()
