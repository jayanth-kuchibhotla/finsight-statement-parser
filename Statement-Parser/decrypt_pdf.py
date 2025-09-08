import pikepdf
from datetime import datetime

# Bank-specific password rules
BANK_PASSWORD_PATTERNS = {
    "hdfc": [
        lambda dob, acc, cust, pan, mob: dob.strftime("%d%m%Y") if dob else None,
        lambda dob, acc, cust, pan, mob: cust,
    ],
    "sbi": [
        lambda dob, acc, cust, pan, mob: dob.strftime("%d%m%Y") if dob else None,
        lambda dob, acc, cust, pan, mob: acc[-5:] if acc else None,  # last 5 digits
    ],
    "icici": [
        lambda dob, acc, cust, pan, mob: acc,
        lambda dob, acc, cust, pan, mob: dob.strftime("%d%m%Y") if dob else None,
    ],
    "axis": [
        lambda dob, acc, cust, pan, mob: cust,
        lambda dob, acc, cust, pan, mob: dob.strftime("%d%m%Y") if dob else None,
    ],
    "kotak": [
        lambda dob, acc, cust, pan, mob: dob.strftime("%d%m%Y") if dob else None,
        lambda dob, acc, cust, pan, mob: acc[-6:] if acc else None,  # last 6 digits
    ],
    "hdfc_cc": [  # HDFC Credit Card statements
        lambda dob, acc, cust, pan, mob: pan,
        lambda dob, acc, cust, pan, mob: mob[-4:] if mob else None,
    ],
}

def try_bank_passwords(filepath, decrypted_filepath, bank, dob=None, acc=None, cust=None, pan=None, mob=None):
    """
    Try to decrypt a bank statement PDF using known password patterns.
    """
    verdict = False
    output_password = None
    state = None

    # 1. Try without password (maybe not encrypted)
    try:
        pdf = pikepdf.open(filepath)
        pdf.save(decrypted_filepath)
        return ("not_encrypted", True, None)
    except pikepdf.PasswordError:
        state = "encrypted"

    # 2. Try each password pattern for that bank
    for gen_pwd in BANK_PASSWORD_PATTERNS.get(bank.lower(), []):
        try:
            password = gen_pwd(dob, acc, cust, pan, mob)
            if password:
                pdf = pikepdf.open(filepath, password=str(password))
                pdf.save(decrypted_filepath)
                return (state, True, password)
        except pikepdf.PasswordError:
            continue

    # 3. If none worked
    return (state, False, None)
