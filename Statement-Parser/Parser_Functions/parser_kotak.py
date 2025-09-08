import pdfplumber
import pandas as pd
from datetime import datetime
import re

def parser_kotak_fun(filepath):
    """
    Parses a Kotak Mahindra bank statement PDF and extracts transaction data.

    Args:
        filepath (str): The path to the PDF file.

    Returns:
        tuple: A tuple containing:
            - str: "without_timestamps"
            - dict: A dictionary with statement-level information.
            - list: A list of dictionaries, where each dictionary represents a transaction.
    """
    datetimes, descriptions, amounts, balances, types = [], [], [], [], []

    with pdfplumber.open(filepath) as pdf:
        pages_count = len(pdf.pages)
        
        # Extract statement-level info (from first page)
        first_page_text = pdf.pages[0].extract_text()
        
        account_number, customer_name, date_start, date_end, branch = None, None, None, None, None

        # Extract Account Number
        acc_num_match = re.search(r"Account No\s*:\s*(\d+)", first_page_text)
        if acc_num_match:
            account_number = acc_num_match.group(1)

        # Extract Customer Name
        cust_name_match = re.search(r"Name\s*:\s*(.*)", first_page_text)
        if cust_name_match:
            customer_name = cust_name_match.group(1).strip()

        # Extract Statement Period
        period_match = re.search(r"Statement for the period\s*:\s*(\d{2}-\d{2}-\d{4})\s*to\s*(\d{2}-\d{2}-\d{4})", first_page_text)
        if period_match:
            date_start = datetime.strptime(period_match.group(1), "%d-%m-%Y").strftime("%Y-%m-%d")
            date_end = datetime.strptime(period_match.group(2), "%d-%m-%Y").strftime("%Y-%m-%d")
            
        # Extract Branch
        branch_match = re.search(r"Branch\s*:\s*(.*)", first_page_text)
        if branch_match:
            branch = branch_match.group(1).strip()


        # Extract transactions (all pages)
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                # Identify transaction rows based on date format dd-mm-yyyy
                if re.match(r'^\d{2}-\d{2}-\d{4}', line):
                    parts = line.split()
                    
                    # Date
                    txn_date = datetime.strptime(parts[0], "%d-%m-%Y").strftime("%Y-%m-%d")
                    
                    # Description
                    desc_parts = []
                    i = 2 # start after value date
                    while i < len(parts) and not re.match(r'[\d,]+\.\d{2}', parts[i]):
                        desc_parts.append(parts[i])
                        i += 1
                    description = " ".join(desc_parts)
                    
                    # Debit/Credit and Balance
                    amount_str = parts[i]
                    balance_str = parts[i+1]

                    if "(Cr)" in amount_str:
                        amount = float(amount_str.replace('(Cr)', '').replace(',', ''))
                        txn_type = 'credit'
                    else:
                        amount = -float(amount_str.replace('(Dr)', '').replace(',', ''))
                        txn_type = 'debit'
                        
                    datetimes.append(txn_date)
                    descriptions.append(description)
                    amounts.append(amount)
                    balances.append(float(balance_str.replace(',', '')))
                    types.append(txn_type)


    # Build DataFrame (optional, but can be useful for data manipulation)
    output = pd.DataFrame({
        "Transaction Date": datetimes,
        "Description": descriptions,
        "Amount": amounts,
        "Balance": balances,
        "Transaction Type": types
    })

    # Statement summary
    output_statement = {
        "bank_code": "kotak",
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
