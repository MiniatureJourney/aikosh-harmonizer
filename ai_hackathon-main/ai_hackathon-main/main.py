from pdf_service.orchestrator import process_pdf
import json

result = process_pdf("sample.pdf")

with open("outputs/output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("PDF processed successfully")
