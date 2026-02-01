import os
import json
import glob
from dotenv import load_dotenv
from google import genai
from ingester import extract_file_info  # Import your working ingester logic
from pdf_service.metadata_generator import get_prioritized_models, generate_metadata_with_retry

# --- 1. SETUP & CONFIG ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
    print("WARNING: GEMINI_API_KEY not found. Harmonization will fail.")

def _generate_with_retry_harmonizer(model_id, prompt, max_retries=3):
    """Thin wrapper so harmonizer can use same retry logic; metadata_generator has its own client."""
    return generate_metadata_with_retry(model_id, prompt, max_retries)

def get_aikosh_metadata(raw_data):
    """
    Sends raw metadata to Gemma and forces it to return an AIKosh-compatible JSON.
    Uses robust fallback logic.
    """
    
    prompt = f"""
    Act as a Senior Data Architect for the **India Data Management Office (IDMO)**.
    Standardize the following raw metadata from a structured dataset (CSV/Excel) into a strictly compliant JSON object.

    RAW INPUT:
    - Filename: {raw_data.filename}
    - Headers: {raw_data.columns}
    - Data Preview (First 5 rows): 
    {raw_data.sample_data}

    ---
    STANDARDIZATION RULES:
    1. **Sector**: MUST be one of: [Agriculture, Education, Healthcare, Finance, Energy, Transport, Urban Development, Rural Development, Law & Justice, Science & Tech, Environment, Governance].
    2. **Ministry**: Infer the Central or State Ministry responsible for this data.
    3. **Granularity**: Analyse columns. If 'Dist_Code' exists -> Granularity is 'District'. If 'State_Code' -> 'State'.
    4. **Dates**: Normalize date ranges to ISO format (YYYY-MM-DD).
    5. **Headers**: You MUST map every original column to a standardized, clean snake_case name.

    OUTPUT JSON STRUCTURE (IDMO Compliant):
    {{
        "catalog_info": {{
            "title": "Formal Descriptive Title",
            "description": "Concise summary of the dataset's contents and utility.",
            "sector": "Standard Sector from list",
            "keywords": ["tag1", "tag2", "tag3"]
        }},
        "provenance": {{
            "source": "Ministry/Department Name",
            "jurisdiction": "State/District or 'India'",
            "data_owner": "Agency Name"
        }},
        "spatial_temporal": {{
            "temporal_range": "YYYY-YYYY",
            "spatial_coverage": "Region Name",
            "granularity": "National/State/District/Village"
        }},
        "technical_metadata": {{
            "format": "CSV/Excel",
            "schema_details": [{{ "column": "original_col_name", "standardized_header": "Standardized_Name", "type": "String/Int/Float", "description": "What this column represents" }}],
            "ai_readiness_level": 0.9,
            "machine_readable": true
        }}
    }}

    INSTRUCTIONS:
    - Map EVERY original column to a "standardized_header" (Snake Case, Descriptive).
    - Example: "Dist_nm" -> "District_Name", "pop_2011" -> "Population_Census_2011".
    - Output ONLY valid JSON.
    """
    
    if not client:
        print("CRITICAL ERROR: GEMINI_API_KEY is missing/invalid. Cannot contact AI.")
        return {"error": "All models failed (Missing API Key)", "details": "Please set GEMINI_API_KEY in Render Environment Variables"}

    candidates = get_prioritized_models(client)
    last_err = None

    for model_id in candidates:
        try:
            response = _generate_with_retry_harmonizer(model_id, prompt)
            if not response: continue
            
            raw_text = response.text.strip()
            
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
                
            return json.loads(raw_text.strip())
            
        except Exception as e:
            print(f"Model {model_id} failed: {e}")
            last_err = e
            continue
            
    return {"error": "All models failed", "details": str(last_err)}

# --- 4. EXECUTION BLOCK ---
if __name__ == "__main__":
    # Look for files in your 'uploads/' directory as shown in your folder schema
    files = glob.glob("uploads/*.csv")
    
    if not files:
        print("No files found in 'uploads/'. Please check your folder path.")
    
    for file_path in files:
        print(f"\n[STEP 1] Ingesting: {os.path.basename(file_path)}...")
        raw_info = extract_file_info(file_path) # Uses your working ingester
        
        print("[STEP 2] Harmonizing with Gemma API...")
        final_metadata = get_aikosh_metadata(raw_info)
        
        print("\n--- FINAL AIKOSH COMPATIBLE METADATA ---")
        print(json.dumps(final_metadata, indent=2))
        
        # Optional: Save to a JSON file for your hackathon submission
        output_name = f"metadata_{raw_info.filename.replace('.csv', '.json')}"
        with open(output_name, "w") as f:
            json.dump(final_metadata, f, indent=2)
        print(f"Saved to: {output_name}")