"""
Tests for pdf_converter module.
"""
import json
import pytest
from pathlib import Path
from processor.converters.markdown_converter import markdown_to_pdf
from processor.converters.pdf_converter import pdf_to_svg, svg_to_png


def test_pdf_to_svg(example_markdown_file, temp_output_dir):
    """Test converting PDF to SVG with embedded data."""
    # First create a PDF to test with
    pdf_file = markdown_to_pdf(example_markdown_file, temp_output_dir)
    
    # Convert PDF to SVG
    svg_path, metadata = pdf_to_svg(pdf_file, temp_output_dir)
    
    # Check if SVG was created
    assert svg_path.exists()
    assert svg_path.suffix == ".svg"
    assert svg_path.stat().st_size > 0
    
    # Check metadata
    assert "file" in metadata
    assert str(svg_path) == metadata["file"]
    assert metadata["pdf_embedded"] is True
    assert "pages" in metadata
    assert metadata["pages"] == []


def test_svg_to_png(example_markdown_file, temp_output_dir):
    """Test converting embedded PDF in SVG to PNG."""
    # First create a PDF and then SVG to test with
    pdf_file = markdown_to_pdf(example_markdown_file, temp_output_dir)
    svg_path, metadata = pdf_to_svg(pdf_file, temp_output_dir)
    
    # Convert SVG to PNG
    png_files, updated_metadata = svg_to_png(svg_path, metadata, temp_output_dir)
    
    # Check if PNG files were created
    assert len(png_files) > 0
    for png_info in png_files:
        png_path = Path(png_info["file"])
        assert png_path.exists()
        assert png_path.suffix == ".png"
        assert png_path.stat().st_size > 0
    
    # Check metadata was updated
    assert len(updated_metadata["pages"]) == len(png_files)
    assert updated_metadata["total_pages"] == len(png_files)
