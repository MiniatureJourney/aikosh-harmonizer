import pdfplumber
import fitz  # PyMuPDF fallback when pdfplumber fails

def extract_text(pdf_path: str) -> list:
    """Extract text from digital PDF. Tries pdfplumber first, then PyMuPDF (fitz) as fallback."""
    pages = _extract_with_pdfplumber(pdf_path)
    if pages and any(p.get("text", "").strip() for p in pages):
        return pages
    # Fallback: many PDFs work better with PyMuPDF (e.g. embedded fonts, odd encodings)
    return _extract_with_fitz(pdf_path)


def _extract_with_pdfplumber(pdf_path: str) -> list:
    try:
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                except Exception:
                    text = None
                pages.append({"page": i + 1, "text": (text or "").strip()})
        return pages
    except Exception:
        return []


def _extract_with_fitz(pdf_path: str) -> list:
    """Fallback text extraction using PyMuPDF (fitz). More reliable for some PDFs."""
    doc = None
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            pages.append({"page": i + 1, "text": text})
        return pages
    except Exception:
        return []
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
