"""
Main document processor class that orchestrates the document processing pipeline.
"""

import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime

from ..converters.markdown_converter import create_example_markdown, markdown_to_pdf
from ..converters.pdf_converter import pdf_to_svg, svg_to_png
from ..utils.ocr_processor import process_ocr
from ..utils.file_utils import search_svg_files
from ..utils.html_utils import enclose_to_html_table
from ..utils.metadata_utils import save_metadata


class DocumentProcessor:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metadata = {}

    def create_example_markdown(self):
        """Create an example markdown file."""
        return create_example_markdown(self.output_dir)

    def markdown_to_pdf(self, md_file):
        """Convert markdown to PDF."""
        return markdown_to_pdf(md_file, self.output_dir)

    def pdf_to_svg(self, pdf_file):
        """Convert PDF to SVG with embedded data and metadata."""
        svg_path, metadata = pdf_to_svg(pdf_file, self.output_dir)
        self.metadata.update(metadata)
        return svg_path, self.metadata

    def svg_to_png(self, svg_file, metadata):
        """Convert embedded PDF to PNG and update metadata."""
        png_files, metadata = svg_to_png(svg_file, metadata, self.output_dir)
        self.metadata.update(metadata)
        return png_files, self.metadata

    def process_ocr(self, png_files, metadata):
        """Process PNG files with OCR and update metadata."""
        updated_metadata = process_ocr(png_files, metadata)
        self.metadata.update(updated_metadata)
        return self.metadata

    def search_svg_files(self, search_path="."):
        """Search filesystem for SVG files and their metadata."""
        return search_svg_files(search_path)

    def enclose_to_html_table(self, svg_files_data):
        """Create HTML table with SVG thumbnails."""
        html_path = self.output_dir / "dashboard.html"
        return enclose_to_html_table(svg_files_data, html_path)

    def save_metadata(self, metadata, filename="metadata.json"):
        """Save metadata to JSON file."""
        return save_metadata(metadata, self.output_dir, filename)
