from pdf_service.detector import detect_pdf_type
from pdf_service.text_extractor import extract_text
from pdf_service.ocr_extractor import ocr_pdf
from pdf_service.table_extractor import extract_tables
from pdf_service.junk_cleaner import clean_pages
from pdf_service.semantic_mapper import semantic_map
from pdf_service.confidence_scorer import score_confidence
from pdf_service.metadata_generator import generate_metadata
from pdf_service.lineage_tracker import track_lineage

def process_pdf(pdf_path: str):
    pdf_type = detect_pdf_type(pdf_path)

    if pdf_type == "digital":
        pages = extract_text(pdf_path)
        tables = extract_tables(pdf_path)
    else:
        pages = ocr_pdf(pdf_path)
        tables = []

    clean_pages_data = clean_pages(pages)
    semantic = semantic_map(tables)
    confidence = score_confidence(clean_pages_data, tables)
    metadata = generate_metadata(clean_pages_data)
    lineage = track_lineage(pdf_path, confidence)

    return {
        "pdf_type": pdf_type,
        "pages": clean_pages_data,
        "tables": tables,
        "semantic": semantic,
        "confidence": confidence,
        "metadata": metadata,
        "lineage": lineage
    }
