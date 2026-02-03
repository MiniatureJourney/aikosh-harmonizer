import easyocr
import fitz # PyMuPDF
import numpy as np
from PIL import Image
import os
import gc

# Low Memory Mode for Render (disables OCR to stay < 512MB)
LOW_MEMORY_MODE = os.getenv("LOW_MEMORY_MODE", "false").lower() == "true"

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
                if LOW_MEMORY_MODE:
                    print(f"[Page {i+1}] LOW_MEMORY_MODE active. Skipping OCR.")
                    pages.append({
                        "page": i + 1,
                        "text": "[OCR Skipped due to Low Memory Mode]"
                    })
                    continue
                reader = get_reader() # Load model only if needed

            # Optimization: 150 DPI is sufficient for most LLM tasks and saves RAM
            pix = page.get_pixmap(dpi=150) 
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
    finally:
        # Cleanup reader if not needed anymore to free RAM
        # In LOW_MEMORY_MODE, we aggressively clear it after EVERY file.
        # Even without LOW_MEMORY_MODE, clearing it is safer for shared workers.
        global _reader
        if _reader is not None:
             del _reader
             _reader = None
             gc.collect()

