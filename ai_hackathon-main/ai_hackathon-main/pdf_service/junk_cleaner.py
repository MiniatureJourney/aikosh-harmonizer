from collections import Counter
import re

def clean_pages(pages):
    lines_per_page = [p["text"].split("\n") for p in pages]
    all_lines = [line.strip() for page in lines_per_page for line in page]

    cleaned_pages = []

    # Skip frequency-based cleaning for single-page documents

    # because every line would appear in 100% of pages (1/1) and be removed
    if len(pages) > 1:
        freq = Counter(all_lines)

        for p in pages:
            cleaned = []
            for line in p["text"].split("\n"):
                line = line.strip()
                if freq[line] > len(pages) * 0.6:
                    continue
                if re.match(r"^Page \d+", line):
                    continue
                cleaned.append(line)

            cleaned_pages.append({
                "page": p["page"],
                "text": "\n".join(cleaned)
            })
    else:
        # Just simple cleaning without frequency check
        for p in pages:
            cleaned = []
            for line in p["text"].split("\n"):
                line = line.strip()
                if re.match(r"^Page \d+", line):
                    continue
                cleaned.append(line)
            
            cleaned_pages.append({
                "page": p["page"],
                "text": "\n".join(cleaned)
            })

    return cleaned_pages

