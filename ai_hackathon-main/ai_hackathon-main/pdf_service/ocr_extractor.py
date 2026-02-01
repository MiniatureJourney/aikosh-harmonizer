import easyocr
import fitz # PyMuPDF
import numpy as np
from PIL import Image

# Global variable for lazy loading
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        print("Lazy loading EasyOCR Model...")
        # gpu=False significantly reduces memory overhead on CPU-only envs like Render Free Tier
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def ocr_pdf(pdf_path: str):
    pages = []
    
    try:
        reader = None # Delay loading reader until absolutely necessary
        doc = fitz.open(pdf_path)
        
        for i, page in enumerate(doc):
            # HYBRID STRATEGY: Try instant text extraction first
            text_content = page.get_text().strip()
            
            # If significant text found (e.g. > 10 chars), skip OCR
            if len(text_content) > 10:
                print(f"[Page {i+1}] Digital text found. Skipping OCR.")
                pages.append({
                    "page": i + 1,
                    "text": text_content
                })
                continue
            
            # Fallback to OCR
            print(f"[Page {i+1}] No text found. Running OCR...")
            
            if reader is None:
                reader = get_reader() # Load model only if needed

            # Optimization: 200 DPI is usually sufficient for text
            pix = page.get_pixmap(dpi=200) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img)
            
            # detail=0 returns just the text
            result = reader.readtext(img_np, detail=0, paragraph=True)
            text_content = " ".join(result)
            
            pages.append({
                "page": i + 1,
                "text": text_content
            })
            
        doc.close()
        return pages

    except Exception as e:
        print(f"Error in OCR extraction: {e}")
        return []

