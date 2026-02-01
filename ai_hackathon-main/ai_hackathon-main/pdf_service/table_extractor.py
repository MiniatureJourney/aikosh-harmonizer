import camelot

def extract_tables(pdf_path: str):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
    except Exception:
        return []

    extracted = []
    for i, table in enumerate(tables):
        # Convert to list of lists (much easier for frontend to render)
        # to_dict('split') returns {'index': [], 'columns': [], 'data': [[row1], [row2]]}
        # We just want the data including headers if possible, or just raw values.
        # camelot dataframe usually lacks headers unless parsed. 
        # We'll use values.tolist() which gives the raw grid.
        data_grid = table.df.values.tolist()
        
        extracted.append({
            "table_id": i,
            "page": table.page,
            "accuracy": table.accuracy, # Real metadata
            "whitespace": table.whitespace,
            "order": table.order,
            "data": data_grid # Array of Arrays
        })

    return extracted
