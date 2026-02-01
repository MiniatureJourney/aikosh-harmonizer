import easyocr
import fitz # PyMuPDF
import numpy as np
from PIL import Image

# Initialize Reader once to be reused
reader = easyocr.Reader(['en'])

def ocr_pdf(pdf_path: str):
    pages = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for i, page in enumerate(doc):
            # Render page to image (zoom=2 for better OCR quality)
            # matrix = fitz.Matrix(2, 2) 
            # pix = page.get_pixmap(matrix=matrix)
            pix = page.get_pixmap(dpi=300) # 300 DPI is good standard
            
            # Convert PyMuPDF Pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert PIL image to numpy array which EasyOCR accepts
            img_np = np.array(img)
            
            # detail=0 returns just the text, paragraph=True combines lines
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

