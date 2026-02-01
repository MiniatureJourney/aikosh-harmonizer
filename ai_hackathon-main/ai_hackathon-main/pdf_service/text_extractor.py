import pdfplumber

def extract_text(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            pages.append({
                "page": i + 1,
                "text": text or ""
            })
    return pages
