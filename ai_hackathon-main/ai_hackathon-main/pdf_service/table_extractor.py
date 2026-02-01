import camelot

def extract_tables(pdf_path: str):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
    except Exception:
        return []

    extracted = []
    for i, table in enumerate(tables):
        extracted.append({
            "table_id": i,
            "data": table.df.to_dict()
        })

    return extracted
