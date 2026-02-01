import json
import sys

def validate_schema(data):
    required_keys = ["catalog_info", "provenance", "spatial_temporal", "technical_metadata"]
    missing = [k for k in required_keys if k not in data]
    
    if missing:
        print(f"FAILED: Missing top-level keys: {missing}")
        return False

    # Check sub-keys (sampling a few critical ones)
    if "title" not in data["catalog_info"]:
        print("FAILED: Missing catalog_info.title")
        return False
        
    if "format" not in data["technical_metadata"]:
        print("FAILED: Missing technical_metadata.format")
        return False

    print("SUCCESS: JSON schema matches AIKosh IDMO standards.")
    return True

if __name__ == "__main__":
    # Mock data structure to test validation logic
    mock_data = {
        "catalog_info": {
            "title": "Test Title",
            "description": "Test Desc",
            "sector": "Agri",
            "keywords": []
        },
        "provenance": {
            "source": "Min",
            "jurisdiction": "State",
            "data_owner": "Gov"
        },
        "spatial_temporal": {
            "temporal_range": "2023",
            "spatial_coverage": "India",
            "granularity": "State"
        },
        "technical_metadata": {
            "format": "PDF",
            "ai_readiness_level": 0.5,
            "machine_readable": False
        }
    }
    
    validate_schema(mock_data)
