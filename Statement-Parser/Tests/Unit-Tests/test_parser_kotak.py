import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Parser_Functions')))

from parser_kotak import parser_kotak_fun

class TestParserKotak(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_parser_kotak_fun(self, mock_pdfplumber_open):
        # Mock the PDF content
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
            Account No : 987654321098
            Name : Alice Wonderland
            Statement for the period : 01-04-2023 to 30-04-2023
            Branch : BANGALORE
            Date Value Date Description Debit/Credit Balance
            02-04-2023 02-04-2023 SALARY 80,000.00(Cr) 80,000.00
            08-04-2023 08-04-2023 SHOPPING 3,000.00(Dr) 77,000.00
        """
        mock_pdf.pages = [mock_page1]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        status, statement_info, transactions = parser_kotak_fun('dummy.pdf')

        # Assertions
        self.assertEqual(status, "without_timestamps")
        
        # Statement info assertions
        self.assertEqual(statement_info['bank_code'], 'kotak')
        self.assertEqual(statement_info['account_number'], '987654321098')
        self.assertEqual(statement_info['user_name'], 'Alice Wonderland')
        self.assertEqual(statement_info['statement_start'], '2023-04-01')
        self.assertEqual(statement_info['statement_end'], '2023-04-30')
        self.assertEqual(statement_info['bank_branch'], 'BANGALORE')

        # Transactions assertions
        self.assertEqual(len(transactions), 2)
        
        # First transaction
        self.assertEqual(transactions[0]['date'], '2023-04-02')
        self.assertEqual(transactions[0]['description'], 'SALARY')
        self.assertEqual(transactions[0]['amount'], 80000.00)
        self.assertEqual(transactions[0]['balance'], 80000.00)
        self.assertEqual(transactions[0]['transaction_type'], 'credit')

        # Second transaction
        self.assertEqual(transactions[1]['date'], '2023-04-08')
        self.assertEqual(transactions[1]['description'], 'SHOPPING')
        self.assertEqual(transactions[1]['amount'], -3000.00)
        self.assertEqual(transactions[1]['balance'], 77000.00)
        self.assertEqual(transactions[1]['transaction_type'], 'debit')

if __name__ == '__main__':
    unittest.main()
