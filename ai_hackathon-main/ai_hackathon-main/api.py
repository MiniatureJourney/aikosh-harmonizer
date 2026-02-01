from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import uuid
from services.storage import get_storage_service
from services.database import get_db_service
from services.tasks import process_file_task
from pdf_service.cache_manager import get_file_hash
import uvicorn
from typing import List, Dict, Any

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AIKosh Harmonizer – Commercial API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Request ID middleware (commercial: trace requests)
@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
storage = get_storage_service()
db = get_db_service()

# Config (Render: set MAX_UPLOAD_MB if needed; free tier often allows ~25MB request body)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
@app.head("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Service is healthy",
        "mode": "Async" if USE_CELERY else "Sync",
        "max_upload_mb": MAX_UPLOAD_MB,
    }

@app.post("/harmonize")
@limiter.limit("30/minute")
async def harmonize_endpoint(request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    return await handle_upload(file, "harmonize", background_tasks)

@app.post("/process-pdf")
@limiter.limit("30/minute")
async def process_pdf_endpoint(request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    return await handle_upload(file, "pdf", background_tasks)

async def handle_upload(file: UploadFile, task_type: str, background_tasks: BackgroundTasks):
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_UPLOAD_MB}MB. Your file: {len(content) / (1024*1024):.1f}MB.",
        )

    file_hash = get_file_hash(content)

    # 2. Check DB (Cache)
    cached = db.get_metadata(file_hash)
    if cached:
        print(f"Cache Hit: {file_hash} Status: {cached.get('status')}")
        
        # FIX: If it's stuck in "processing" for a re-upload, it's likely a zombie job.
        # We should force re-process it.
        if cached.get("status") == "success":
             return cached
        elif cached.get("status") == "error":
             # Optional: retry if user wants, but for now return error
             pass 
        else:
             # Status is "processing" (or None) but user submitted again.
             # Assume zombie -> Fall through to dispatch new task.
             print("Stale 'processing' job found. Re-queueing...")
             pass

    # 3. Upload to Storage (S3 or Local)
    # We use file_hash + extension as unique name
    ext = os.path.splitext(file.filename)[1]
    storage_filename = f"{file_hash}{ext}"
    
    try:
        storage.save(content, storage_filename)
        
        # 4. Dispatch Task
        # Initial status
        db.save_metadata(file_hash, {"status": "processing", "file_hash": file_hash, "original_filename": file.filename})

        if USE_CELERY:
            # Phase 2: Async Worker
            process_file_task.delay(file_hash, storage_filename, task_type)
        else:
            # Fallback: BackgroundTasks (Phase 1.5)
            # This runs in the same process but after response is sent (if we return) 
            # OR we can just await it for "Simple" mode users who don't want polling.
            # To support the "Polling" UI, we MUST return immediately.
            background_tasks.add_task(process_file_task, file_hash, storage_filename, task_type)

        return {"status": "processing", "file_hash": file_hash, "message": "File uploaded, processing started."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{file_hash}")
async def get_status(file_hash: str):
    data = db.get_metadata(file_hash)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return data

def _idmo_from_metadata(metadata: dict) -> dict:
    """Get IDMO blob: for harmonize it's top-level; for PDF it's under 'metadata'."""
    return metadata.get("metadata") or metadata


@app.get("/download-harmonized/{file_hash}")
async def download_harmonized(file_hash: str):
    metadata = db.get_metadata(file_hash)
    if not metadata or metadata.get("status") == "processing":
        raise HTTPException(status_code=404, detail="File not ready or not found")

    ext = os.path.splitext(metadata.get("original_filename", "data.csv"))[1] or ".csv"
    storage_filename = f"{file_hash}{ext}"

    try:
        content = storage.get(storage_filename)
    except Exception:
        raise HTTPException(status_code=404, detail="Source file not found in storage")

    # Safe temp file per request (no collision with concurrent requests)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix="aikosh_dl_")
    temp_input = tmp.name
    try:
        tmp.write(content)
        tmp.close()
    except Exception:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        raise HTTPException(status_code=500, detail="Failed to write temp file")

    temp_used_as_response = False
    try:
        import pandas as pd
        idmo = _idmo_from_metadata(metadata)
        tech = idmo.get("technical_metadata", {})
        cat = idmo.get("catalog_info", {})

        if ext not in ('.csv', '.xlsx', '.xls'):
            temp_used_as_response = True
            orig_name = metadata.get("original_filename") or ("download" + ext)
            return FileResponse(temp_input, filename=orig_name)

        if ext == '.csv':
            df = pd.read_csv(temp_input)
        else:
            df = pd.read_excel(temp_input)

        schema = tech.get("schema_details", [])
        rename_map = {item["column"]: item["standardized_header"] for item in schema if "column" in item}
        if rename_map:
            df.rename(columns=rename_map, inplace=True)

        output_filename = f"harmonized_{cat.get('title', 'data')}.csv"
        output_filename = "".join([c for c in output_filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip() or "harmonized_data.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        df.to_csv(output_path, index=False)

        return FileResponse(output_path, filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if not temp_used_as_response and os.path.exists(temp_input):
            try:
                os.remove(temp_input)
            except OSError:
                pass

@app.post("/synthesize")
async def synthesize_endpoint(metadata_list: List[Dict[Any, Any]]):
    from synthesizer import synthesize_metadata
    try:
        return synthesize_metadata(metadata_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

