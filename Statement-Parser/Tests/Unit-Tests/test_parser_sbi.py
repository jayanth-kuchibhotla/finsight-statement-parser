import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Parser_Functions')))

from parser_sbi import parser_sbi_fun

class TestParserSbi(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_parser_sbi_fun(self, mock_pdfplumber_open):
        # Mock the PDF content
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
            Account No : 112233445566
            Branch : CHENNAI
            Customer Name : Bob Johnson
            Statement Period : 01/05/2023 to 31/05/2023
            Date Description Debit Credit Balance
            02/05/23 SALARY - 90,000.00 90,000.00
            09/05/23 EMI 4,000.00 - 86,000.00
        """
        mock_pdf.pages = [mock_page1]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        status, statement_info, transactions = parser_sbi_fun('dummy.pdf')

        # Assertions
        self.assertEqual(status, "without_timestamps")
        
        # Statement info assertions
        self.assertEqual(statement_info['bank_code'], 'sbi')
        self.assertEqual(statement_info['account_number'], '112233445566')
        self.assertEqual(statement_info['user_name'], 'Bob Johnson')
        self.assertEqual(statement_info['statement_start'], '2023-05-01')
        self.assertEqual(statement_info['statement_end'], '2023-05-31')
        self.assertEqual(statement_info['bank_branch'], 'CHENNAI')

        # Transactions assertions
        self.assertEqual(len(transactions), 2)
        
        # First transaction
        self.assertEqual(transactions[0]['date'], '2023-05-02')
        self.assertEqual(transactions[0]['description'], 'SALARY')
        self.assertEqual(transactions[0]['amount'], 90000.00)
        self.assertEqual(transactions[0]['balance'], 90000.00)
        self.assertEqual(transactions[0]['transaction_type'], 'credit')

        # Second transaction
        self.assertEqual(transactions[1]['date'], '2023-05-09')
        self.assertEqual(transactions[1]['description'], 'EMI')
        self.assertEqual(transactions[1]['amount'], -4000.00)
        self.assertEqual(transactions[1]['balance'], 86000.00)
        self.assertEqual(transactions[1]['transaction_type'], 'debit')

if __name__ == '__main__':
    unittest.main()
