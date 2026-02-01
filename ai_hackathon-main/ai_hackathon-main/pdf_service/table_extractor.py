import camelot
import math

def _clean_cell(cell):
    """Normalize a table cell: strip whitespace, NaN/None -> empty string."""
    if cell is None or (isinstance(cell, float) and math.isnan(cell)):
        return ""
    s = str(cell).strip()
    return s

def extract_tables(pdf_path: str):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
    except Exception:
        return []

    extracted = []
    for i, table in enumerate(tables):
        data_grid = table.df.values.tolist()
        # Clean malformed cells: strip, normalize NaN/None
        cleaned_grid = [[_clean_cell(c) for c in row] for row in data_grid]

        extracted.append({
            "table_id": i,
            "page": table.page,
            "accuracy": table.accuracy,
            "whitespace": table.whitespace,
            "order": table.order,
            "data": cleaned_grid,
        })

    return extracted
