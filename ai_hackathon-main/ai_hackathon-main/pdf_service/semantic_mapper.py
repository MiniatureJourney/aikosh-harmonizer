def semantic_map(tables):
    mappings = {}
    
    # Standard IDMO Schema Dictionary
    SCHEMA_MAP = {
        # Temporal
        "year": "temporal_year", "yr": "temporal_year", "period": "temporal_period",
        "date": "temporal_date", "dt": "temporal_date", "dob": "date_of_birth",
        # Spatial
        "state": "spatial_state", "dist": "spatial_district", "district": "spatial_district",
        "vill": "spatial_village", "taluk": "spatial_subdistrict", "tehsil": "spatial_subdistrict",
        # Identifiers
        "id": "record_id", "sno": "serial_number", "sl_no": "serial_number",
        "name": "entity_name", "beneficiary": "beneficiary_name",
        # Metrics
        "pop": "population", "amount": "financial_amount", "rs": "financial_amount_inr"
    }

    mapped_count = 0
    total_cols = 0

    for table in tables:
        # Tables now have 'data' as List of Lists. 
        # Assume First Row is header
        if not table.get("data"): continue
        
        headers = table["data"][0]
        total_cols += len(headers)
        
        for col in headers:
            col_str = str(col).lower().strip().replace(".", "").replace("_", " ")
            
            # Check dictionary
            standardized = None
            for key, val in SCHEMA_MAP.items():
                if key in col_str: # Simple containment match
                    standardized = val
                    break
            
            if standardized:
                mappings[col] = standardized
                mapped_count += 1
            else:
                # Fallback normalization
                mappings[col] = col_str.replace(" ", "_")

    # Calculate "Semantic Confidence" based on how many columns we understood
    confidence = 0.5 # Base
    if total_cols > 0:
        confidence = 0.5 + (0.5 * (mapped_count / total_cols))

    return {
        "column_mappings": mappings,
        "semantic_confidence": round(confidence, 2)
    }
