import argparse
import html
import json
import os
from datetime import datetime, timezone

from pypdf import PdfReader


def convert_pdf_to_html_pages(pdf_path: str, output_dir: str, title: str) -> dict:
    reader = PdfReader(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        safe_text = html.escape(text).replace("\n", "<br/>")

        filename = f"page_{i}.html"
        out_path = os.path.join(output_dir, filename)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">")
            f.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
            f.write(f"<title>{html.escape(title)} — Page {i}</title>")
            f.write("<style>")
            f.write("body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;margin:0;background:#f9fafb;color:#111827}")
            f.write(".wrap{max-width:900px;margin:0 auto;padding:32px}")
            f.write(".card{background:#fff;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,.08);padding:24px}")
            f.write("h1{margin:0 0 12px 0;font-size:22px}")
            f.write(".meta{color:#6b7280;font-size:14px;margin-bottom:16px}")
            f.write(".content{white-space:normal}")
            f.write("</style>")
            f.write("</head><body><div class=\"wrap\"><div class=\"card\">")
            f.write(f"<h1>{html.escape(title)} — Page {i}</h1>")
            f.write(f"<div class=\"meta\">Generated {datetime.now(timezone.utc).isoformat()}</div>")
            f.write(f"<div class=\"content\">{safe_text}</div>")
            f.write("</div></div></body></html>")

        pages.append({"page": i, "file": filename})

    return {"pages": pages, "pageCount": len(pages)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    result = convert_pdf_to_html_pages(args.pdf, args.out, args.title)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
