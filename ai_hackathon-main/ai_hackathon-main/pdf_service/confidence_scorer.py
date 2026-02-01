def score_confidence(pages, tables):
    """
    Calculates a composite confidence score (0.0 - 1.0) based on extraction quality.
    """
    score = 1.0
    
    # 1. Text Extractor Confidence
    # Proxy: Text density. If pages correspond to empty strings, confidence drops.
    total_len = sum(len(p.get("text", "")) for p in pages)
    if total_len < 50: 
        score *= 0.5 # Suspiciously empty
    elif total_len < 200:
        score *= 0.8 # Probably sparse

    # 2. Table Confidence
    # Proxy: "Whiteness". If tables are mostly empty cells, confidence drops.
    if tables:
        for t in tables:
            # t['whitespace'] is a value from Camelot (0-100) representing empty area
            # High whitespace = sparse table = lower confidence in structure
            if t.get("whitespace", 0) > 80:
                score *= 0.9

    # 3. Penalize if NO structured data found at all
    if not pages and not tables:
        return 0.0

    return round(max(score, 0.1), 2)
