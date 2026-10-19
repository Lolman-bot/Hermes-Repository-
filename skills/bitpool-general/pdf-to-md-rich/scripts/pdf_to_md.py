#!/usr/bin/env python3
"""Convert one PDF to Markdown via pymupdf4llm, OCR'ing image-only pages first if needed.

Usage:
    python pdf_to_md.py <input.pdf> <output.md> [--images-dir DIR] [--ocr auto|force|skip]

Prints "OK ocr=<yes|no> pages=<n>" on success, or "ERROR <message>" to stderr and exits 1.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF
import pymupdf4llm


def needs_ocr(pdf_path, min_chars_per_page=20):
    doc = fitz.open(pdf_path)
    try:
        pages_with_text = sum(1 for p in doc if len(p.get_text().strip()) >= min_chars_per_page)
        return pages_with_text < doc.page_count
    finally:
        doc.close()


def run_ocr(src_path, dst_path):
    result = subprocess.run(
        ["ocrmypdf", "--skip-text", "--quiet", src_path, dst_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not os.path.exists(dst_path):
        raise RuntimeError(f"ocrmypdf failed: {result.stderr.strip()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf_path")
    ap.add_argument("md_path")
    ap.add_argument("--images-dir", default=None)
    ap.add_argument("--ocr", choices=["auto", "force", "skip"], default="auto")
    args = ap.parse_args()

    source_pdf = args.pdf_path
    ocr_used = False
    tmp_dir = None

    try:
        do_ocr = args.ocr == "force" or (args.ocr == "auto" and needs_ocr(source_pdf))
        if do_ocr:
            tmp_dir = tempfile.mkdtemp(prefix="pdf2md-ocr-")
            ocr_pdf = os.path.join(tmp_dir, "ocr.pdf")
            run_ocr(source_pdf, ocr_pdf)
            source_pdf = ocr_pdf
            ocr_used = True

        kwargs = {}
        if args.images_dir:
            os.makedirs(args.images_dir, exist_ok=True)
            kwargs["write_images"] = True
            kwargs["image_path"] = args.images_dir

        md_text = pymupdf4llm.to_markdown(source_pdf, **kwargs)
        with open(args.md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        doc = fitz.open(args.pdf_path)
        page_count = doc.page_count
        doc.close()
        print(f"OK ocr={'yes' if ocr_used else 'no'} pages={page_count}")
    except Exception as e:
        print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
