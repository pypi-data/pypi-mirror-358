"""
PDF conversion utilities.
"""

import base64
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from pdf2image import convert_from_path


def pdf_to_svg(pdf_file, output_dir):
    """Convert PDF to SVG with embedded data and metadata."""
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

    svg_path = output_dir / "invoice_example.svg"
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


def svg_to_png(svg_file, metadata, output_dir):
    """Convert embedded PDF to PNG and update metadata."""
    # First convert PDF to images
    pdf_file = output_dir / "invoice_example.pdf"
    images = convert_from_path(pdf_file, dpi=150)

    png_files = []
    for i, image in enumerate(images):
        png_path = output_dir / f"page_{i + 1}.png"
        image.save(png_path, 'PNG')

        # Convert PNG to base64
        with open(png_path, 'rb') as f:
            png_data = base64.b64encode(f.read()).decode('utf-8')

        png_files.append({
            "page": i + 1,
            "file": str(png_path),
            "base64": png_data,
            "size": png_path.stat().st_size
        })

        print(f"Created: {png_path}")

    # Update metadata
    metadata["pages"] = png_files
    metadata["total_pages"] = len(png_files)

    return png_files, metadata
