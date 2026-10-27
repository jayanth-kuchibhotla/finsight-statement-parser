import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os
import pikepdf

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from decrypt_pdf import try_bank_passwords

class TestDecryptPdf(unittest.TestCase):

    @patch('pikepdf.open')
    def test_try_bank_passwords_not_encrypted(self, mock_pikepdf_open):
        # Mock a non-encrypted PDF
        mock_pdf = MagicMock()
        mock_pikepdf_open.return_value = mock_pdf

        result_state, result_verdict, result_password = try_bank_passwords('dummy.pdf', 'decrypted.pdf', 'hdfc')

        self.assertEqual(result_state, "not_encrypted")
        self.assertTrue(result_verdict)
        self.assertIsNone(result_password)
        mock_pdf.save.assert_called_once_with('decrypted.pdf')

    @patch('pikepdf.open')
    def test_try_bank_passwords_encrypted_success(self, mock_pikepdf_open):
        # Mock an encrypted PDF that opens with the correct password
        mock_pdf = MagicMock()
        mock_pikepdf_open.side_effect = [
            pikepdf.PasswordError("wrong password"),  # First call without password fails
            mock_pdf  # Second call with correct password succeeds
        ]

        dob = datetime(2000, 1, 1)
        result_state, result_verdict, result_password = try_bank_passwords(
            'dummy.pdf', 'decrypted.pdf', 'hdfc', fullname = "John Doe", dob = dob
        )

        self.assertEqual(result_state, "encrypted")
        self.assertTrue(result_verdict)
        self.assertEqual(result_password, "01012000")
        mock_pdf.save.assert_called_once_with('decrypted.pdf')

    @patch('pikepdf.open', side_effect=pikepdf.PasswordError("wrong password"))
    def test_try_bank_passwords_encrypted_fail(self, mock_pikepdf_open):
        # Mock an encrypted PDF where all password attempts fail
        dob = datetime(2000, 1, 1)
        result_state, result_verdict, result_password = try_bank_passwords(
            'dummy.pdf', 'decrypted.pdf', 'hdfc', dob=dob
        )

        self.assertEqual(result_state, "encrypted")
        self.assertFalse(result_verdict)
        self.assertIsNone(result_password)

if __name__ == '__main__':
    unittest.main()
