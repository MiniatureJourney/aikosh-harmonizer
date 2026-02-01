import fitz

def detect_pdf_type(pdf_path: str) -> str:
    """Detect scanned (image-based) vs digital (text-based) PDF. Safe for corrupted/invalid PDFs."""
    doc = None
    try:
        doc = fitz.open(pdf_path)
        total_text = 0
        total_images = 0
        for page in doc:
            total_text += len(page.get_text().strip())
            total_images += len(page.get_images())
        if total_text < 200 and total_images > 0:
            return "scanned"
        return "digital"
    except Exception as e:
        raise RuntimeError(f"PDF detection failed: {e}") from e
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
