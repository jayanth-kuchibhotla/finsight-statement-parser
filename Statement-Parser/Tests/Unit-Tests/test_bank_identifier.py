import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bank_identifier import identify_bank

class TestBankIdentifier(unittest.TestCase):

    @patch('pdfplumber.open')
    def test_identify_bank(self, mock_pdfplumber_open):
        # Mock the PDF content for different banks
        pdf_mocks = {
            "hdfc": "This is an HDFC Bank statement.",
            "icici": "Welcome to ICICI Bank.",
            "axis": "Axis Bank Limited.",
            "kotak": "Kotak Mahindra Bank.",
            "sbi": "State Bank of India.",
            "unknown": "Some other bank."
        }

        for bank, text in pdf_mocks.items():
            with self.subTest(bank=bank):
                # Create a mock PDF object
                mock_pdf = MagicMock()
                mock_page = MagicMock()
                mock_page.extract_text.return_value = text
                mock_pdf.pages = [mock_page]
                
                # Configure the context manager
                mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

                # Call the function with a dummy path
                result = identify_bank('dummy_path.pdf')
                self.assertEqual(result, bank)

    @patch('pdfplumber.open', side_effect=Exception("Failed to open PDF"))
    def test_identify_bank_exception(self, mock_pdfplumber_open):
        result = identify_bank('dummy_path.pdf')
        self.assertEqual(result, "unknown")

if __name__ == '__main__':
    unittest.main()
