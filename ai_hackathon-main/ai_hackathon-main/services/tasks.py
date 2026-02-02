import os
import tempfile
import gc
import shutil
from typing import Dict, Any
from celery_app import celery_app
from services.storage import get_storage_service
from services.database import get_db_service

# Import core logic (existing files)
# We assume these are in the python path (root dir)
import sys
sys.path.append(os.getcwd()) # Ensure root is in path

from ingester import extract_file_info
from harmonizer import get_aikosh_metadata
from pdf_service.orchestrator import process_pdf

def _idmo_blob(data: dict) -> dict:
    """Get the IDMO metadata blob (for harmonize it's top-level; for PDF it's under 'metadata')."""
    return data.get("metadata") or data

@celery_app.task(bind=True)
def process_file_task(self, file_hash: str, filename: str, task_type: str = "harmonize"):
    """
    Background task to process a file.
    1. Downloads file from Storage (S3/Local).
    2. Runs processing (Harmonize or PDF).
    3. Saves result to Database (Postgres/JSON).
    """
    storage = get_storage_service()
    db = get_db_service()

    # Safe temp file: filename may contain path separators on some systems
    ext = os.path.splitext(filename)[1] or ".bin"
    fd, temp_path = tempfile.mkstemp(suffix=ext, prefix="aikosh_worker_")
    os.close(fd)
    
    try:
        print(f"[Worker] Processing {filename} ({task_type})")
        
        # 1. Download from Storage (Streaming)
        stream = storage.get_stream(filename)
        try:
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(stream, f)
        finally:
            if hasattr(stream, 'close'):
                stream.close()
            
        result_metadata = {}

        # 2. Process
        print(f"[Worker] Step 1: Processing started for {task_type}")
        if task_type == "harmonize":
            # Excel/CSV
            print(f"[Worker] Step 2: Extracting info from {temp_path}")
            raw_info = extract_file_info(temp_path)
            # Need to patch the filename in raw_info because temp_path is ugly
            raw_info.filename = filename 
            
            print(f"[Worker] Step 3: Calling Harmonizer (AI)")
            result_metadata = get_aikosh_metadata(raw_info)
            print(f"[Worker] Step 4: Harmonization Complete")
            
        elif task_type == "pdf":
            print(f"[Worker] Step 2: Orchestrating PDF")
            # PDF Orchestrator
            result = process_pdf(temp_path)
            # Save FULL result (tables, lineage, etc)
            result_metadata = result
            print(f"[Worker] Step 3: PDF Complete")

        # Add tracking info
        result_metadata["file_hash"] = file_hash
        result_metadata["original_filename"] = filename
        result_metadata["_worker_processed"] = True

        # CRITICAL: explicit status update for frontend polling
        # For PDF, error can be in result_metadata["metadata"], top-level, or _errors from orchestrator
        print(f"[Worker] Step 5: Checking for errors in result")
        idmo = _idmo_blob(result_metadata)
        pdf_errors = result_metadata.pop("_errors", None)  # list of per-stage errors
        has_error = (
            pdf_errors
            or "error" in result_metadata
            or result_metadata.get("title") == "Processing Error"
            or "error" in idmo
            or idmo.get("title") == "Processing Error"
        )
        if has_error:
            result_metadata["status"] = "error"
            result_metadata["error_message"] = (
                "; ".join(pdf_errors)
                if pdf_errors
                else result_metadata.get("error")
                or result_metadata.get("summary")
                or idmo.get("error")
                or idmo.get("summary")
                or "Processing failed"
            )
            print(f"[Worker] Failure Detected: {result_metadata['error_message']}")
        else:
            result_metadata["status"] = "success"
        
        # 3. Save to DB
        print(f"[Worker] Step 6: Saving to DB")
        db.save_metadata(file_hash, result_metadata)
        print(f"[Worker] Finished {filename}")
        
        return result_metadata

    except Exception as e:
        print(f"[Worker] Error processing {filename}: {e}")
        # Save error state to DB so frontend knows it failed
        error_meta = {
            "file_hash": file_hash,
            "status": "error", 
            "error_message": str(e)
        }
        db.save_metadata(file_hash, error_meta)
        raise e
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Explicit GC
        gc.collect()
