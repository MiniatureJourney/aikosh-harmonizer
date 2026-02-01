from pdf_service.detector import detect_pdf_type
from pdf_service.text_extractor import extract_text
from pdf_service.junk_cleaner import clean_pages
import os



# Use correct relative path from pdf_service directory
pdf_path = os.path.abspath("../uploads/Branchwise_operational_perf_4.pdf")

print(f"Testing PDF: {pdf_path}")



try:
    with open("reproduce_log.txt", "w") as f:
        f.write(f"Testing PDF: {pdf_path}\n")
        pdf_type = detect_pdf_type(pdf_path)
        f.write(f"Detected PDF type: {pdf_type}\n")
        
        if pdf_type == "digital":
            f.write("Attempting extract_text...\n")
            pages = extract_text(pdf_path)
            for page in pages:
                f.write(f"Page {page['page']} text length: {len(page['text'])}\n")
                f.write(f"Page {page['page']} text content: '{page['text']}'\n")
            
            f.write("Cleaning pages...\n")
            cleaned_pages = clean_pages(pages)
            for page in cleaned_pages:
                f.write(f"Cleaned Page {page['page']} text length: {len(page['text'])}\n")
                f.write(f"Cleaned Page {page['page']} text content: '{page['text']}'\n")

        else:
            f.write("Detected as scanned, would use OCR (skipping for reproduction).\n")

except Exception as e:
    with open("reproduce_log.txt", "a") as f:
        f.write(f"Error: {e}\n")

