import datetime

def track_lineage(filename, confidence):
    return {
        "source": filename,
        "processed_at": datetime.datetime.utcnow().isoformat(),
        "confidence": confidence
    }
