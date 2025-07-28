import fitz  # PyMuPDF
import json
import os

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    title = ""
    headings = []
    font_sizes = {}

    # Step 1: Analyze font sizes
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = round(span["size"], 1)
                        font_sizes[size] = font_sizes.get(size, 0) + 1

    sorted_sizes = sorted(font_sizes.items(), key=lambda x: (-x[1], -x[0]))
    h1_size, h2_size, h3_size = [size for size, _ in sorted_sizes[:3]]

    # Step 2: Extract headings
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    span = line["spans"][0]
                    size = round(span["size"], 1)
                    text = " ".join([s["text"] for s in line["spans"] if s["text"].strip()])
                    if not text:
                        continue

                    level = ""
                    if size == h1_size:
                        level = "H1"
                    elif size == h2_size:
                        level = "H2"
                    elif size == h3_size:
                        level = "H3"

                    if level:
                        if not title and level == "H1":
                            title = text
                        headings.append({
                            "level": level,
                            "text": text,
                            "page": page_num + 1
                        })

    return {
        "title": title if title else "Untitled",
        "outline": headings
    }

def save_output(result, output_path):
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    input_dir = "./input"
    output_dir = "./output"


    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            result = extract_headings(os.path.join(input_dir, file))
            save_output(result, os.path.join(output_dir, file.replace(".pdf", ".json")))
