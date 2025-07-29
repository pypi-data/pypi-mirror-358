#!/usr/bin/env python3
"""
Document Processing Pipeline
Handles: Markdown → PDF → SVG → PNG → OCR → Search → Aggregation
"""

import os
import json
import base64
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

# Core libraries
import markdown
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from weasyprint import HTML, CSS

# Image processing
from PIL import Image
import cairosvg
from pdf2image import convert_from_path
import pytesseract

# Web processing
from bs4 import BeautifulSoup


class DocumentProcessor:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metadata = {}

    def create_example_markdown(self):
        """Step 1: Create example markdown file"""
        markdown_content = """# Invoice Example

## Invoice #INV-2025-001

**Date:** June 25, 2025  
**Due Date:** July 25, 2025

### Bill To:
**Customer Name:** John Smith  
**Address:** 123 Main Street  
**City:** New York, NY 10001

### Services Provided:

| Item | Description | Quantity | Rate | Amount |
|------|-------------|----------|------|--------|
| 1 | Web Development | 40 hrs | $100/hr | $4,000 |
| 2 | Design Services | 20 hrs | $80/hr | $1,600 |
| 3 | Consultation | 10 hrs | $120/hr | $1,200 |

### Summary:
- **Subtotal:** $6,800
- **Tax (8.5%):** $578
- **Total:** $7,378

### Payment Terms:
Payment is due within 30 days of invoice date.

### Notes:
Thank you for your business!
"""

        file_path = self.output_dir / "invoice_example.md"
        with open(file_path, 'w') as f:
            f.write(markdown_content)

        print(f"Created: {file_path}")
        return file_path

    def markdown_to_pdf(self, md_file):
        """Step 2: Convert markdown to PDF"""
        with open(md_file, 'r') as f:
            md_content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables'])

        # Add CSS styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h1, h2 {{ color: #333; }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """

        pdf_path = self.output_dir / "invoice_example.pdf"
        HTML(string=styled_html).write_pdf(pdf_path)

        print(f"Created: {pdf_path}")
        return pdf_path

    def pdf_to_svg(self, pdf_file):
        """Step 3: Convert PDF to SVG with embedded data and metadata"""
        # Read PDF as base64
        with open(pdf_file, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        # Create SVG with embedded PDF data
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="800" height="1000" viewBox="0 0 800 1000">

    <!-- Metadata -->
    <metadata>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:Description rdf:about="">
                <dc:title>Invoice Example</dc:title>
                <dc:creator>Document Processor</dc:creator>
                <dc:date>{datetime.now().isoformat()}</dc:date>
                <dc:description>Generated invoice PDF embedded in SVG</dc:description>
            </rdf:Description>
        </rdf:RDF>
    </metadata>

    <!-- Background -->
    <rect width="100%" height="100%" fill="white"/>

    <!-- PDF Data (base64 encoded) -->
    <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">
            <embed src="data:application/pdf;base64,{pdf_data}" 
                   width="100%" height="100%" type="application/pdf"/>
        </div>
    </foreignObject>

    <!-- Visual representation -->
    <text x="50" y="50" font-family="Arial" font-size="24" fill="black">Invoice Document</text>
    <rect x="50" y="70" width="700" height="2" fill="#333"/>
    <text x="50" y="120" font-family="Arial" font-size="16" fill="gray">
        PDF content embedded as data URI
    </text>
</svg>"""

        svg_path = self.output_dir / "invoice_example.svg"
        with open(svg_path, 'w') as f:
            f.write(svg_content)

        # Create JSON metadata
        metadata = {
            "file": str(svg_path),
            "type": "svg_with_pdf",
            "created": datetime.now().isoformat(),
            "pdf_embedded": True,
            "pdf_size": len(pdf_data),
            "pages": [],
            "ocr_data": []
        }

        print(f"Created: {svg_path}")
        return svg_path, metadata

    def svg_to_png(self, svg_file, metadata):
        """Step 4: Convert embedded PDF to PNG and update metadata"""
        # First convert PDF to images
        pdf_file = self.output_dir / "invoice_example.pdf"
        images = convert_from_path(pdf_file, dpi=150)

        png_files = []
        for i, image in enumerate(images):
            png_path = self.output_dir / f"page_{i + 1}.png"
            image.save(png_path, 'PNG')

            # Convert PNG to base64
            with open(png_path, 'rb') as f:
                png_data = base64.b64encode(f.read()).decode('utf-8')

            png_files.append({
                "page": i + 1,
                "file": str(png_path),
                "base64": png_data,
                "size": os.path.getsize(png_path)
            })

            print(f"Created: {png_path}")

        # Update metadata
        metadata["pages"] = png_files
        metadata["total_pages"] = len(png_files)

        return png_files, metadata

    def process_ocr(self, png_files, metadata):
        """Step 5: Process PNG files with OCR and update metadata"""
        for page_info in png_files:
            try:
                # Perform OCR
                image = Image.open(page_info["file"])
                ocr_text = pytesseract.image_to_string(image)

                # Extract structured data
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

                page_info["ocr_text"] = ocr_text.strip()
                page_info["ocr_confidence"] = sum(ocr_data['conf']) / len([x for x in ocr_data['conf'] if x > 0])
                page_info["word_count"] = len(ocr_text.split())

                print(f"OCR processed: {page_info['file']}")

            except Exception as e:
                print(f"OCR failed for {page_info['file']}: {e}")
                page_info["ocr_text"] = ""
                page_info["ocr_confidence"] = 0

        metadata["ocr_data"] = png_files
        return metadata

    def search_svg_files(self, search_path="."):
        """Step 6: Search filesystem for SVG files and their metadata"""
        svg_files = []
        search_dir = Path(search_path)

        for svg_file in search_dir.rglob("*.svg"):
            try:
                with open(svg_file, 'r') as f:
                    content = f.read()

                # Parse SVG for metadata
                soup = BeautifulSoup(content, 'xml')
                metadata_elem = soup.find('metadata')

                file_info = {
                    "path": str(svg_file),
                    "size": svg_file.stat().st_size,
                    "modified": datetime.fromtimestamp(svg_file.stat().st_mtime).isoformat(),
                    "has_metadata": metadata_elem is not None,
                    "has_pdf_data": 'data:application/pdf;base64,' in content
                }

                if metadata_elem:
                    title_elem = soup.find('dc:title')
                    if title_elem:
                        file_info["title"] = title_elem.get_text()

                svg_files.append(file_info)
                print(f"Found SVG: {svg_file}")

            except Exception as e:
                print(f"Error processing {svg_file}: {e}")

        return svg_files

    def aggregate_to_html_table(self, svg_files_data):
        """Step 7: Create HTML table with SVG thumbnails"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>SVG Files Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .thumbnail { width: 200px; height: 150px; border: 1px solid #ccc; }
        .metadata { font-size: 12px; color: #666; }
        .svg-preview { max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>
    <h1>SVG Files Dashboard</h1>
    <table>
        <thead>
            <tr>
                <th>Thumbnail</th>
                <th>File Path</th>
                <th>Size</th>
                <th>Modified</th>
                <th>Has PDF</th>
                <th>Metadata</th>
            </tr>
        </thead>
        <tbody>
"""

        for svg_data in svg_files_data:
            # Create thumbnail
            thumbnail_html = f'<div class="thumbnail">SVG Preview</div>'
            if os.path.exists(svg_data["path"]):
                try:
                    with open(svg_data["path"], 'r') as f:
                        svg_content = f.read()
                    # Embed SVG directly as thumbnail
                    thumbnail_html = f'<div class="thumbnail">{svg_content}</div>'
                except:
                    pass

            has_pdf = "✓" if svg_data.get("has_pdf_data") else "✗"
            has_metadata = "✓" if svg_data.get("has_metadata") else "✗"
            title = svg_data.get("title", "No title")

            html_content += f"""
            <tr>
                <td>{thumbnail_html}</td>
                <td><a href="file://{svg_data['path']}">{svg_data['path']}</a></td>
                <td>{svg_data['size']} bytes</td>
                <td>{svg_data['modified']}</td>
                <td>{has_pdf}</td>
                <td class="metadata">
                    Metadata: {has_metadata}<br>
                    Title: {title}
                </td>
            </tr>
            """

        html_content += """
        </tbody>
    </table>
</body>
</html>
"""

        html_path = self.output_dir / "dashboard.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

        print(f"Created dashboard: {html_path}")

        # Open in browser
        webbrowser.open(f"file://{html_path.absolute()}")

        return html_path

    def save_metadata(self, metadata, filename="metadata.json"):
        """Save metadata to JSON file"""
        json_path = self.output_dir / filename
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata: {json_path}")
        return json_path


def main():
    parser = argparse.ArgumentParser(description="Document Processing Pipeline")
    parser.add_argument("--step", choices=["create", "process", "aggregate", "search"],
                        required=True, help="Processing step to execute")
    parser.add_argument("--output", default="output", help="Output directory")

    args = parser.parse_args()

    processor = DocumentProcessor(args.output)

    if args.step == "create":
        # Step 1: Create example
        processor.create_example_markdown()

    elif args.step == "process":
        # Steps 2-5: Full processing pipeline
        md_file = processor.output_dir / "invoice_example.md"
        if not md_file.exists():
            md_file = processor.create_example_markdown()

        pdf_file = processor.markdown_to_pdf(md_file)
        svg_file, metadata = processor.pdf_to_svg(pdf_file)
        png_files, metadata = processor.svg_to_png(svg_file, metadata)
        metadata = processor.process_ocr(png_files, metadata)
        processor.save_metadata(metadata)

    elif args.step == "search":
        # Step 6: Search for SVG files
        svg_files = processor.search_svg_files()
        processor.save_metadata(svg_files, "svg_search_results.json")

    elif args.step == "aggregate":
        # Step 7: Create dashboard
        svg_files = processor.search_svg_files()
        processor.aggregate_to_html_table(svg_files)


if __name__ == "__main__":
    main()