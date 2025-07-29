"""
Tests for ocr_processor module.
"""
import pytest
from pathlib import Path
from processor.converters.markdown_converter import markdown_to_pdf
from processor.converters.pdf_converter import pdf_to_svg, svg_to_png
from processor.utils.ocr_processor import process_ocr


def test_process_ocr(example_markdown_file, temp_output_dir):
    """Test OCR processing of PNG files."""
    # Setup: Create PDF, SVG, and PNG files
    pdf_file = markdown_to_pdf(example_markdown_file, temp_output_dir)
    svg_path, metadata = pdf_to_svg(pdf_file, temp_output_dir)
    png_files, metadata = svg_to_png(svg_path, metadata, temp_output_dir)
    
    # Process OCR
    updated_metadata = process_ocr(png_files, metadata)
    
    # Check if OCR data was added to metadata
    assert "ocr_data" in updated_metadata
    assert len(updated_metadata["ocr_data"]) == len(png_files)
    
    # Check each page's OCR data
    for page in updated_metadata["ocr_data"]:
        assert "ocr_text" in page
        assert "ocr_confidence" in page
        assert "word_count" in page
        
        # Basic validation of OCR results
        assert isinstance(page["ocr_text"], str)
        assert isinstance(page["ocr_confidence"], float)
        assert isinstance(page["word_count"], int)
        
        # For the test document, we should have some text
        if page["ocr_text"]:  # Only check if OCR found text
            assert page["word_count"] > 0
            assert 0 <= page["ocr_confidence"] <= 100
