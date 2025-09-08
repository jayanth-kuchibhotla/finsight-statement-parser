import pdfplumber

def identify_bank(pdf_path):
    """
    Identifies the bank from a PDF statement.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The bank name in lowercase (e.g., "hdfc", "icici"), or "unknown".
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()
            
            if "HDFC Bank" in first_page_text:
                return "hdfc"
            elif "ICICI Bank" in first_page_text:
                return "icici"
            elif "Axis Bank" in first_page_text:
                return "axis"
            elif "Kotak Mahindra Bank" in first_page_text:
                return "kotak"
            elif "State Bank of India" in first_page_text:
                return "sbi"
            else:
                return "unknown"
    except Exception as e:
        # Log the error
        print(f"Error identifying bank: {e}")
        return "unknown"
