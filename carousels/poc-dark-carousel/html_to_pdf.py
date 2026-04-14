#!/usr/bin/env python3
"""
Convert an HTML carousel (with .slide divs) to a PDF.
Uses Playwright to screenshot each slide at 1080x1350, then combines via fpdf2.
"""

import subprocess
import sys
import os
from pathlib import Path

# Auto-install fpdf2 if needed
try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
    from fpdf import FPDF

from playwright.sync_api import sync_playwright

SLIDE_W = 1080
SLIDE_H = 1350


def html_to_pdf(html_path: str, output_pdf: str):
    html_path = Path(html_path).resolve()
    output_pdf = Path(output_pdf).resolve()
    png_dir = output_pdf.parent / "slides_png"
    png_dir.mkdir(parents=True, exist_ok=True)

    print(f"Opening {html_path}...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": SLIDE_W, "height": SLIDE_H})
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")

        # Find all slides
        slides = page.query_selector_all(".slide")
        print(f"Found {len(slides)} slides")

        png_files = []
        for i, slide in enumerate(slides):
            png_path = png_dir / f"slide-{i+1:02d}.png"
            slide.screenshot(path=str(png_path))
            png_files.append(png_path)
            print(f"  Captured slide {i+1}: {png_path.name}")

        browser.close()

    # Combine PNGs into PDF
    # PDF dimensions: 1080x1350 pixels at 72 DPI = 381mm x 476.25mm
    # But we use mm units scaled to fit nicely
    pdf_w_mm = 150  # mm
    pdf_h_mm = pdf_w_mm * (SLIDE_H / SLIDE_W)  # maintain 4:5 ratio

    pdf = FPDF(unit="mm", format=(pdf_w_mm, pdf_h_mm))
    pdf.set_auto_page_break(False)

    for png_path in png_files:
        pdf.add_page()
        pdf.image(str(png_path), x=0, y=0, w=pdf_w_mm, h=pdf_h_mm)

    pdf.output(str(output_pdf))
    print(f"\nPDF saved: {output_pdf}")
    print(f"PNGs saved in: {png_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        html_file = Path(__file__).parent / "poc-carousel.html"
        pdf_file = Path(__file__).parent / "poc-carousel.pdf"
    elif len(sys.argv) == 2:
        html_file = sys.argv[1]
        pdf_file = Path(sys.argv[1]).with_suffix(".pdf")
    else:
        html_file = sys.argv[1]
        pdf_file = sys.argv[2]

    html_to_pdf(str(html_file), str(pdf_file))
