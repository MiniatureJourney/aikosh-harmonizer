import camelot
import math

def _clean_cell(cell):
    """Normalize a table cell: strip whitespace, NaN/None -> empty string."""
    if cell is None or (isinstance(cell, float) and math.isnan(cell)):
        return ""
    s = str(cell).strip()
    return s

def extract_tables(pdf_path: str) -> list:
    """Extract tables from PDF. Returns [] on any failure (Camelot can fail on many PDFs)."""
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
    except Exception:
        return []

    extracted = []
    for i, table in enumerate(tables):
        try:
            data_grid = table.df.values.tolist()
            cleaned_grid = [[_clean_cell(c) for c in row] for row in data_grid]
            extracted.append({
                "table_id": i,
                "page": getattr(table, "page", i + 1),
                "accuracy": getattr(table, "accuracy", 0),
                "whitespace": getattr(table, "whitespace", 0),
                "order": getattr(table, "order", 0),
                "data": cleaned_grid,
            })
        except Exception:
            continue
    return extracted
