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

from pdf_service.metadata_generator import get_prioritized_models, generate_metadata_with_retry

def synthesize_metadata(metadata_list):
    """
    Takes a list of metadata JSON objects and synthesizes them into a single
    consolidated metadata record using Gemini.
    """
    if not client:
        return {"error": "GEMINI_API_KEY not found"}

    if not metadata_list:
        return {"error": "No metadata provided for synthesis"}

    # Prepare the input for the LLM
    input_text = json.dumps(metadata_list, indent=2)
    
    prompt = f"""
    Act as a Senior Data Architect for the **India Data Management Office (IDMO)**.
    You are provided with a list of metadata records extracted from related Indian Government documents.
    
    YOUR TASK:
    Synthesize these into a SINGLE Master Metadata Record that represents the *entire collection*.
    
    RULES FOR SYNTHESIS:
    1. **Title**: If parts are "Annual Report Part 1" & "Part 2", Master Title is "Annual Report 2024".
    2. **Sector**: Must be one of standard OGD sectors (Agriculture, Education, etc.).
    3. **Spatial**: Find the broadest coverage. If one is "Mumbai" and another "Pune", coverage is "Maharashtra".
    4. **Temporal**: Create a range from the Earliest Start Date to the Latest End Date.
    5. **Ministry**: Ensure the Ministry name is standardized and expanded.
    
    INPUT METADATA LIST:
    {input_text}

    OUTPUT JSON STRUCTURE (IDMO Compliant):
    {{
        "catalog_info": {{
            "title": "Consolidated Master Title",
            "description": "Comprehensive summary of the entire collection.",
            "sector": "Standard Sector",
            "keywords": ["merged", "unique", "tags"]
        }},
        "provenance": {{
            "source": "Ministry/Department",
            "jurisdiction": "Broadest Jurisdiction",
            "data_owner": "Primary Agency"
        }},
        "spatial_temporal": {{
            "temporal_range": "YYYY-MM-DD to YYYY-MM-DD",
            "spatial_coverage": "Combined Region",
            "granularity": "State/National"
        }},
        "technical_metadata": {{
            "format": "Consolidated",
            "ai_readiness_level": 0.85,
            "machine_readable": true
        }}
    }}
    
    Return ONLY the raw JSON.
    """

    candidates = get_prioritized_models(client)
    last_error = None
    
    for model_id in candidates:
        try:
            print(f"Synthesizing with model: {model_id}...")
            response = generate_metadata_with_retry(model_id, prompt)
            
            if not response:
                continue
                
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
                
            return json.loads(raw_text.strip())
            
        except Exception as e:
            print(f"Synthesis failed with {model_id}: {e}")
            last_error = e
            continue

    return {"error": f"Synthesis failed across all models. Last error: {str(last_error)}"}
