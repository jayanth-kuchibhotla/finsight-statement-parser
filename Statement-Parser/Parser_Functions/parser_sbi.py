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
        account_number, branch, customer_name, date_start, date_end = None, None, None, None, None

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

        raw_text = ""

        # Extract transactions (all pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            raw_text += page_text + "\n"
            lines = page_text.split("\n")

            for line in lines:
                # Match date at beginning
                if line.strip() and re.match(r"\d{2}/\d{2}/\d{2}", line.strip().split()[0]):
                    parts = line.split()
                    
                    # Date
                    txn_date = datetime.strptime(parts[0], "%d/%m/%y").strftime("%Y-%m-%d")
                    datetimes.append(txn_date)
                    
                    # The last three columns are Debit, Credit, Balance
                    balance = parts[-1]
                    credit = parts[-2]
                    debit = parts[-3]
                    
                    # The description is everything between the date and the debit amount
                    description = " ".join(parts[1:-3])
                    descriptions.append(description)

                    # Assign values
                    if debit != "-":
                        amounts.append(-float(debit.replace(",", "")))
                        types.append("debit")
                    elif credit != "-":
                        amounts.append(float(credit.replace(",", "")))
                        types.append("credit")
                    else:
                        amounts.append(0)
                        types.append("unknown")

                    balances.append(float(balance.replace(",", "")) if balance else None)

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

    return ("without_timestamps", output_statement, output_transactions, raw_text)
