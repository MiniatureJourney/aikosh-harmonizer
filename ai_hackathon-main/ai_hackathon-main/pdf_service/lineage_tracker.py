import datetime

def track_lineage(filename, confidence, method="Standard"):
    return {
        "source": filename,
        "processed_at": datetime.datetime.utcnow().isoformat(),
        "confidence": confidence,
        "extraction_method": method
    }
