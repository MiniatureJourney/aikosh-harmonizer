from pdf_service.detector import detect_pdf_type
from pdf_service.text_extractor import extract_text
from pdf_service.ocr_extractor import ocr_pdf
from pdf_service.table_extractor import extract_tables
from pdf_service.junk_cleaner import clean_pages
from pdf_service.semantic_mapper import semantic_map
from pdf_service.confidence_scorer import score_confidence
from pdf_service.metadata_generator import generate_metadata
from pdf_service.lineage_tracker import track_lineage

def _default_metadata_error(msg: str):
    """Return IDMO-shaped error metadata so frontend and status checks work."""
    return {
        "catalog_info": {"title": "Processing Error", "description": msg, "sector": "Governance", "keywords": []},
        "provenance": {"source": "", "jurisdiction": "", "data_owner": ""},
        "spatial_temporal": {"temporal_range": "", "spatial_coverage": "", "granularity": ""},
        "technical_metadata": {"format": "PDF", "ai_readiness_level": 0, "machine_readable": False},
        "error": msg,
        "summary": msg,
    }

def process_pdf(pdf_path: str):
    """Run PDF pipeline with per-stage error handling so one failure doesn't crash the job."""
    errors = []

    # 1. Detect type
    try:
        pdf_type = detect_pdf_type(pdf_path)
    except Exception as e:
        errors.append(f"Detection: {e}")
        pdf_type = "digital"  # fallback

    # 2. Extract text and tables
    pages = []
    tables = []
    # 2. Extract Text/Tables (Based on type)
    pages = []
    tables = []
    method = "Digital Extraction (PyMuPDF)"
    if pdf_type == "digital":
        try:
            pages = extract_text(pdf_path)  # uses pdfplumber + PyMuPDF fallback
            print(f"[Orchestrator] Digital text extraction completed. Pages found: {len(pages)}")
        except Exception as e:
            errors.append(f"Text extraction: {e}")
            print(f"[Orchestrator] Digital text extraction failed: {e}")
        
        # If still no text (e.g. image-only PDF misdetected as digital), try OCR as last resort
        if not pages or not any(p.get("text", "").strip() for p in pages):
            print("[Orchestrator] Digital extraction empty or no text, attempting OCR fallback.")
            try:
                pages = ocr_pdf(pdf_path)
                if pages:
                    method = "OCR (fallback)"
                    print(f"[Orchestrator] OCR fallback completed. Pages found: {len(pages)}")
            except Exception as e:
                errors.append(f"OCR fallback: {e}")
                print(f"[Orchestrator] OCR fallback failed: {e}")
    else: # pdf_type is not digital (e.g., scanned)
        print("[Orchestrator] Scanned PDF detected, starting OCR...")
        method = "OCR (EasyOCR + Hybrid)"
        try:
            pages = ocr_pdf(pdf_path)
            print(f"[Orchestrator] OCR completed. Pages found: {len(pages)}")
        except Exception as e:
            errors.append(f"OCR: {e}")

    print(f"[Orchestrator] Step 3: Extracting Tables (Camelot)")
    tables = []
    try:
        tables = extract_tables(pdf_path)
        print(f"[Orchestrator] Table extraction completed. Tables found: {len(tables)}")
    except Exception as e:
         print(f"[Orchestrator] Table extraction failed: {e}")
         errors.append(f"Table extraction: {e}")


    if not pages:
        errors.append("No text could be extracted from the PDF (empty or unsupported).")

    # 3. Clean and score
    try:
        clean_pages_data = clean_pages(pages) if pages else []
    except Exception as e:
        errors.append(f"Cleaning: {e}")
        clean_pages_data = pages

    try:
        semantic = semantic_map(tables)
    except Exception as e:
        errors.append(f"Semantic mapping: {e}")
        semantic = {"column_mappings": {}, "semantic_confidence": 0}

    try:
        confidence = score_confidence(clean_pages_data, tables)
    except Exception as e:
        confidence = 0.5

    # 4. Metadata (LLM) – skip if no text to avoid empty prompt
    if not clean_pages_data or not any(p.get("text", "").strip() for p in clean_pages_data):
        metadata = _default_metadata_error("No text could be extracted from the PDF.")
        errors.append(metadata["error"])
    else:
        try:
            metadata = generate_metadata(clean_pages_data)
            if metadata and (metadata.get("error") or metadata.get("title") == "Processing Error"):
                metadata = _default_metadata_error(
                    metadata.get("error") or metadata.get("summary") or "Metadata generation failed"
                )
                errors.append(metadata.get("error", "Metadata generation failed"))
        except Exception as e:
            metadata = _default_metadata_error(str(e))
            errors.append(str(e))

    lineage = track_lineage(pdf_path, confidence, method)

    return {
        "pdf_type": pdf_type,
        "pages": clean_pages_data,
        "tables": tables,
        "semantic": semantic,
        "confidence": confidence,
        "metadata": metadata,
        "lineage": lineage,
        "_errors": errors,
    }
