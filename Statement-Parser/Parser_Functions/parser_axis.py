import pdfplumber
import pandas as pd
from datetime import datetime
import re

def parser_axis_fun(filepath):
    """
    Parses an Axis bank statement PDF and extracts transaction data.

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
        period_match = re.search(r"Statement of account for the period of\s*:\s*(\d{2}-\w{3}-\d{4})\s*to\s*(\d{2}-\w{3}-\d{4})", first_page_text)
        if period_match:
            date_start = datetime.strptime(period_match.group(1), "%d-%b-%Y").strftime("%Y-%m-%d")
            date_end = datetime.strptime(period_match.group(2), "%d-%b-%Y").strftime("%Y-%m-%d")
            
        # Extract Branch
        branch_match = re.search(r"Branch\s*:\s*(.*)", first_page_text)
        if branch_match:
            branch = branch_match.group(1).strip()


        # Extract transactions (all pages)
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                line = line.strip()
                # Identify transaction rows based on date format dd-mmm-yy
                if re.match(r'^\d{2}-\w{3}-\d{2}', line):
                    parts = line.split()
                    
                    # Date
                    txn_date = datetime.strptime(parts[0], "%d-%b-%y").strftime("%Y-%m-%d")
                    
                    # Description
                    desc_parts = []
                    i = 2 # start after chq no
                    while i < len(parts) and not re.match(r'[\d,]+\.\d{2}', parts[i]):
                        desc_parts.append(parts[i])
                        i += 1
                    description = " ".join(desc_parts)
                    
                    # Debit, Credit, Balance
                    debit = parts[i]
                    credit = parts[i+1]
                    balance = parts[i+2]

                    if debit != '0.00':
                        amount = -float(debit.replace(',', ''))
                        txn_type = 'debit'
                    else:
                        amount = float(credit.replace(',', ''))
                        txn_type = 'credit'
                        
                    datetimes.append(txn_date)
                    descriptions.append(description)
                    amounts.append(amount)
                    balances.append(float(balance.replace(',', '')))
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
        "bank_code": "axis",
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
