import os
import hashlib
import json
import shutil
from pathlib import Path

CACHE_DIR = "outputs/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_file_hash(file_content: bytes) -> str:
    """Computes SHA256 hash of the file content."""
    return hashlib.sha256(file_content).hexdigest()

def get_cached_metadata(file_hash: str):
    """Retrieves metadata from cache if it exists."""
    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Add a flag to indicate it came from cache
            if isinstance(data, dict):
                data["_is_cached"] = True
            return data
        except Exception:
            return None
    return None

def save_to_cache(file_hash: str, metadata: dict):
    """Saves metadata to cache."""
    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.json")
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
    except Exception as e:
        print(f"Failed to save to cache: {e}")

def clear_cache():
    """Clears the entire cache directory."""
    try:
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR, exist_ok=True)
        return True
    except Exception:
        return False
