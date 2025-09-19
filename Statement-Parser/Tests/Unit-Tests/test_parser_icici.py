import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Parser_Functions')))

from parser_icici import parser_icici_fun

class TestParserIcici(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_parser_icici_fun(self, mock_pdfplumber_open):
        # Mock the PDF content
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
            Account Number : 000123456789
            Name : Sam Smith
            Statement from 01/03/2023 to 31/03/2023
            Branch : PUNE
            S.No. Value Date Transaction Date Chq.No. Description Withdrawal Deposit Balance
            1 02/03/2023 02/03/2023 - SALARY 0.00 70,000.00 70,000.00
            2 07/03/2023 07/03/2023 - BILL 2,000.00 0.00 68,000.00
        """
        mock_pdf.pages = [mock_page1]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        status, statement_info, transactions = parser_icici_fun('dummy.pdf')

        # Assertions
        self.assertEqual(status, "without_timestamps")
        
        # Statement info assertions
        self.assertEqual(statement_info['bank_code'], 'icici')
        self.assertEqual(statement_info['account_number'], '000123456789')
        self.assertEqual(statement_info['user_name'], 'Sam Smith')
        self.assertEqual(statement_info['statement_start'], '2023-03-01')
        self.assertEqual(statement_info['statement_end'], '2023-03-31')
        self.assertEqual(statement_info['bank_branch'], 'PUNE')

        # Transactions assertions
        self.assertEqual(len(transactions), 2)
        
        # First transaction
        self.assertEqual(transactions[0]['date'], '2023-03-02')
        self.assertEqual(transactions[0]['description'], 'SALARY')
        self.assertEqual(transactions[0]['amount'], 70000.00)
        self.assertEqual(transactions[0]['balance'], 70000.00)
        self.assertEqual(transactions[0]['transaction_type'], 'credit')

        # Second transaction
        self.assertEqual(transactions[1]['date'], '2023-03-07')
        self.assertEqual(transactions[1]['description'], 'BILL')
        self.assertEqual(transactions[1]['amount'], -2000.00)
        self.assertEqual(transactions[1]['balance'], 68000.00)
        self.assertEqual(transactions[1]['transaction_type'], 'debit')

if __name__ == '__main__':
    unittest.main()
