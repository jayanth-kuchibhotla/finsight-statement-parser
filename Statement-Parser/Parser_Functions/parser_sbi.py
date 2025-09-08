import pdfplumber
import pandas as pd
from datetime import datetime
import re

def parser_sbi_fun(filepath):
    datetimes, descriptions, amounts, balances, types = [], [], [], [], []

    with pdfplumber.open(filepath) as pdf:
        pages_count = len(pdf.pages)
        
        # Extract statement-level info (from first page)
        first_page = pdf.pages[0].extract_text().split("\n")
        account_number, branch, customer_name, period = None, None, None, None

        for line in first_page:
            if "Account No" in line:
                account_number = line.split(":")[-1].strip()
            elif "Branch" in line:
                branch = line.split(":")[-1].strip()
            elif "Customer Name" in line:
                customer_name = line.split(":")[-1].strip()
            elif "Statement Period" in line:
                period_text = line.split(":")[-1].strip()
                start, end = [d.strip() for d in period_text.split("to")]
                date_start = datetime.strptime(start, "%d/%m/%Y").strftime("%Y-%m-%d")
                date_end = datetime.strptime(end, "%d/%m/%Y").strftime("%Y-%m-%d")

        # Extract transactions (all pages)
        for page in pdf.pages:
            lines = page.extract_text().split("\n")
            for line in lines:
                # Match date at beginning
                if re.match(r"\d{2}/\d{2}/\d{2}", line.strip().split()[0]):
                    parts = line.split()
                    
                    # Date
                    txn_date = datetime.strptime(parts[0], "%d/%m/%y").strftime("%Y-%m-%d")
                    datetimes.append(txn_date)
                    
                    # Description can span multiple words → capture till we hit numbers
                    desc_parts = []
                    i = 1
                    while i < len(parts) and not re.match(r"[\d,.]+", parts[i]):
                        desc_parts.append(parts[i])
                        i += 1
                    description = " ".join(desc_parts)
                    descriptions.append(description)
                    
                    # Now amounts → Debit, Credit, Balance
                    debit, credit, balance = None, None, None
                    nums = [p.replace(",", "") for p in parts[i:]]
                    
                    if len(nums) >= 3:
                        debit = nums[0] if nums[0] != "-" else None
                        credit = nums[1] if nums[1] != "-" else None
                        balance = nums[2]

                    # Assign values
                    if debit:
                        amounts.append(-float(debit))
                        types.append("debit")
                    elif credit:
                        amounts.append(float(credit))
                        types.append("credit")
                    else:
                        amounts.append(0)
                        types.append("unknown")

                    balances.append(float(balance) if balance else None)

    # Build DataFrame
    output = pd.DataFrame({
        "Transaction Date": datetimes,
        "Description": descriptions,
        "Amount": amounts,
        "Balance": balances,
        "Transaction Type": types
    })

    # Statement summary
    output_statement = {
        "bank_code": "sbi",
        "bank_branch": branch,
        "user_name": customer_name,
        "account_number": account_number,
        "statement_start": date_start,
        "statement_end": date_end,
        "pages_count": pages_count
    }

    # Transaction list
    output_transactions = [
        {
            "date": datetimes[i],
            "description": descriptions[i],
            "amount": amounts[i],
            "balance": balances[i],
            "transaction_type": types[i],
            "rank": i + 1
        }
        for i in range(len(datetimes))
    ]

    return ("without_timestamps", output_statement, output_transactions)
