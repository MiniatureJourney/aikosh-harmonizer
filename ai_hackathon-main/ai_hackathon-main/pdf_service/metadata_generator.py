import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

def get_prioritized_models(client):
    """
    Returns a list of available models sorted by preference.
    We prioritize 'flash' models because they have higher rate limits.
    """
    try:
        models = list(client.models.list())
        available_names = [m.name for m in models]
        
        # 1. Hardcoded priority list (Start with most reliable)
        preferred_order = [
            "gemini-1.5-flash", 
            "gemini-1.5-flash-001", 
            "gemini-1.5-pro", 
            "gemini-1.0-pro",
            "gemini-1.5-flash-8b",
            "gemini-pro"
        ]
        
        candidates = []
        
        # Add preferred models first if they exist
        for pref in preferred_order:
            for name in available_names:
                # remove "models/" prefix for comparison if present in available_names but not in pref
                clean_name = name.replace("models/", "")
                if pref == clean_name:
                    candidates.append(name)

        # 2. Add backups, BUT STRICTLY FILTER OUT specialized models
        # We only want text-generation compatible models
        excluded_keywords = [
            "vision", "embedding", "tts", "audio", "robotics", "computer-use", 
            "image-generation", "imagen", "medlm"
        ]
        
        for name in available_names:
            if "gemini" in name and name not in candidates:
                # Check exclusion list
                if not any(keyword in name for keyword in excluded_keywords):
                    candidates.append(name)
                
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen:
                unique_candidates.append(c)
                seen.add(c)
                
        return unique_candidates if unique_candidates else ["gemini-1.5-flash"]
        
    except Exception as e:
        print(f"Warning: Could not list models ({e}). Defaulting to Flash.")
        return ["gemini-1.5-flash"]

def generate_metadata_with_retry(model_id, prompt, max_retries=5):
    """
    Attempts to generate content with exponential backoff for 429 errors.
    """
    import random
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            return response
        except Exception as e:
            error_str = str(e)
            
            # Handle Rate Limits (429) OR Server Overload (503)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str:
                # Exponential backoff: 2, 4, 8, 16, 32... + jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit/Overload on {model_id}. Retrying in {wait_time:.1f}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            
            # If it's a 400 error (Invalid Argument), fail immediately for this model
            elif "400" in error_str or "INVALID_ARGUMENT" in error_str:
                print(f"Model {model_id} incompatible: {error_str}")
                raise e

            # If it's the last attempt, re-raise
            elif attempt == max_retries - 1:
                raise e
            else:
                # For other errors, wait a bit and retry (might be transient)
                time.sleep(2)
                
    return None

def generate_metadata(pages_data):
    """
    Generates AIKosh-compatible metadata from PDF text using Gemini.
    """
    full_text = " ".join([p.get("text", "") for p in pages_data])
    
    if len(full_text) > 100000:
        full_text = full_text[:100000] + "...(truncated)"

    if not client:
        return {"error": "GEMINI_API_KEY not found in .env"}

    prompt = f"""
    Act as a Senior Data Architect for the **India Data Management Office (IDMO)**.
    Analyze the following text extracted from an Indian Government document and generate a high-precision JSON metadata object.

    DOCUMENT TEXT (Truncated):
    {full_text}

    ---
    STANDARDIZATION RULES:
    1. **Sector**: MUST be one of: [Agriculture, Education, Healthcare, Finance, Energy, Transport, Urban Development, Rural Development, Law & Justice, Science & Tech, Environment, Governance]. If unsure, use "Governance".
    2. **Ministry/Department**: Expand abbreviations (e.g., "MoHFW" -> "Ministry of Health and Family Welfare").
    3. **Geography**: Detect specific Indian States, Districts, or "National".
    4. **Granularity**: Choose from [National, State, District, Sub-District, Village].

    OUTPUT JSON STRUCTURE (IDMO Compliant):
    {{
        "catalog_info": {{
            "title": "Formal, descriptive title (e.g., 'Annual Health Survey 2023 - Bihar')",
            "description": "Professional summary including the purpose and scope of the data.",
            "sector": "One of the standard sectors listed above",
            "keywords": ["tag1", "tag2", "tag3"]
        }},
        "provenance": {{
            "source": "Full Name of Ministry or Department",
            "jurisdiction": "Specific State/District or 'India'",
            "data_owner": "Name of the entity/agency (e.g., 'NITI Aayog', 'NHM')"
        }},
        "spatial_temporal": {{
            "temporal_range": "YYYY-MM-DD to YYYY-MM-DD (or 'YYYY-YYYY')",
            "spatial_coverage": "Specific Region Name",
            "granularity": "National/State/District"
        }},
        "technical_metadata": {{
            "format": "PDF",
            "ai_readiness_level": 0.6,
            "machine_readable": false
        }}
    }}

    INSTRUCTIONS:
    - Output ONLY valid JSON.
    - If data is missing, infer reasonable defaults based on context.
    """

    candidates = get_prioritized_models(client)
    last_error = None
    
    if not client:
        print("CRITICAL ERROR: GEMINI_API_KEY is missing. PDF Metadata generation aborted.")
        return {"error": "Missing API Key", "summary": "API Key not found in environment"}

    print(f"Model candidates: {candidates}")

    # Try candidates in order
    for model_id in candidates:
        try:
            print(f"Attempting with model: {model_id}...")
            
            # We retry ONLY the current model for rate limits a few times
            # before giving up and moving to the next model (which might have a separate quota bucket)
            response = generate_metadata_with_retry(model_id, prompt)
            
            if not response:
                continue

            raw_text = getattr(response, "text", None) if response else None
            if not raw_text or not isinstance(raw_text, str):
                # Blocked content or empty response
                last_error = ValueError("LLM returned no text (blocked or empty)")
                continue
            raw_text = raw_text.strip()
            if not raw_text:
                last_error = ValueError("LLM returned empty text")
                continue

            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
            raw_text = raw_text.strip()
            if not raw_text:
                last_error = ValueError("No JSON block in response")
                continue

            return json.loads(raw_text)

        except Exception as e:
            print(f"Failed with {model_id}: {e}")
            last_error = e
            continue

    return {
        "title": "Processing Error",
        "summary": "Could not generate metadata using LLM.",
        "error": f"All models failed. Last error: {str(last_error)}"
    }
