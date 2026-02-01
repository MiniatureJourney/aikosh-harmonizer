import fitz

def detect_pdf_type(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)

    total_text = 0
    total_images = 0

    for page in doc:
        total_text += len(page.get_text().strip())
        total_images += len(page.get_images())

    if total_text < 200 and total_images > 0:
        return "scanned"
    return "digital"
