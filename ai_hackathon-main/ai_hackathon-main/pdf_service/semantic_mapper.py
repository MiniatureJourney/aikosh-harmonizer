def semantic_map(tables):
    mappings = {}

    for table in tables:
        for col in table["data"].keys():
            normalized = str(col).lower().replace(" ", "_").replace("%", "percent")
            mappings[col] = normalized

    return {
        "column_mappings": mappings,
        "confidence": 0.8
    }
