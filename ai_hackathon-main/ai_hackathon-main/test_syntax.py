import traceback
try:
    import pdf_service.ocr_extractor
    print("[OK] ocr_extractor imported")
except Exception as e:
    print(f"[FAIL] ocr_extractor: {e}")
    traceback.print_exc()

try:
    import harmonizer
    print("[OK] harmonizer imported")
except Exception as e:
    print(f"[FAIL] harmonizer: {e}")
    traceback.print_exc()
