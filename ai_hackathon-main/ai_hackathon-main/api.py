from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pdf_service.orchestrator import process_pdf
from pdf_service.cache_manager import get_file_hash, get_cached_metadata, save_to_cache
from harmonizer import get_aikosh_metadata
from synthesizer import synthesize_metadata
from ingester import extract_file_info
import uvicorn
from typing import List, Dict, Any


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="AI Hackathon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    # Serve the index.html
    return FileResponse('static/index.html')

from starlette.concurrency import run_in_threadpool

@app.post("/harmonize")
async def harmonize_endpoint(file: UploadFile = File(...)):
    # 1. Read content for hashing
    content = await file.read()
    file_hash = get_file_hash(content)

    # 2. Check Cache
    cached = get_cached_metadata(file_hash)
    if cached:
        print(f"Returning cached result for {file.filename}")
        return cached # Harmonizer returns direct metadata dict

    # 3. Save file permanently (using hash as ID) for later retrieval/download
    file_ext = os.path.splitext(file.filename)[1]
    saved_filename = os.path.join(UPLOAD_DIR, f"{file_hash}{file_ext}")
    
    with open(saved_filename, "wb") as f:
        f.write(content)

    try:
        # Generate metadata
        # Offload blocking operations to threadpool for smoothness
        raw_info = await run_in_threadpool(extract_file_info, saved_filename)
        metadata = await run_in_threadpool(get_aikosh_metadata, raw_info)
        
        # Add file_hash to metadata for frontend reference
        metadata["file_hash"] = file_hash
        metadata["original_filename"] = file.filename
        
        # 4. Save to Cache
        save_to_cache(file_hash, metadata)
        
        return metadata
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-harmonized/{file_hash}")
async def download_harmonized(file_hash: str):
    # 1. correct file path logic
    # Find the file with any extension
    matching_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(file_hash)]
    if not matching_files:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_path = os.path.join(UPLOAD_DIR, matching_files[0])
    
    # 2. Get Metadata
    metadata = get_cached_metadata(file_hash)
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not found")
        
    # 3. Create Harmonized CSV
    try:
        import pandas as pd
        
        # Read Original
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            return FileResponse(file_path) # Fallback for PDF
            
        # Get Schema Mapping
        schema = metadata.get("technical_metadata", {}).get("schema_details", [])
        rename_map = {}
        for item in schema:
            if "column" in item and "standardized_header" in item:
                rename_map[item["column"]] = item["standardized_header"]
                
        # Apply Renaming
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
            
        # Save to Output
        output_filename = f"harmonized_{metadata.get('catalog_info', {}).get('title', 'data')}.csv"
        # Sanitize filename
        output_filename = "".join([c for c in output_filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        df.to_csv(output_path, index=False)
        
        return FileResponse(output_path, filename=output_filename)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-pdf")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    # 1. Read file content for hashing
    content = await file.read()
    file_hash = get_file_hash(content)
    
    # 2. Check Cache
    cached = get_cached_metadata(file_hash)
    if cached:
        print(f"Returning cached result for {file.filename}")
        return {"metadata": cached}

    # 3. Save temp file for processing (orchestrator expects path)
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as f:
        f.write(content)

    try:
        # Offload blocking PDF operations
        result = await run_in_threadpool(process_pdf, temp_filename)
        
        # 4. Save to Cache
        if result and "metadata" in result:
             # We cache the full result object or just metadata depending on usage.
             # Here we return {metadata: ...} implies 'result' is the full object.
             # Orchestrator returns a dict with 'metadata' key.
             save_to_cache(file_hash, result["metadata"])
             
        return {"metadata": result["metadata"]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/synthesize")
async def synthesize_endpoint(metadata_list: List[Dict[Any, Any]]):
    try:
        if not metadata_list:
            raise HTTPException(status_code=400, detail="No metadata provided")
        
        result = synthesize_metadata(metadata_list)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
