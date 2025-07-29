"""
Tests for file_utils module.
"""
import pytest
from pathlib import Path
from processor.utils.file_utils import search_svg_files


def test_search_svg_files(example_markdown_file, temp_output_dir):
    """Test searching for SVG files."""
    # Create a test SVG file
    svg_file = temp_output_dir / "test.svg"
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <circle cx="50" cy="50" r="40" fill="red"/>
    </svg>"""
    svg_file.write_text(svg_content)
    
    # Search for SVG files
    found_files = search_svg_files(temp_output_dir)
    
    # Check if our test file was found
    assert len(found_files) >= 1
    assert any(f["path"] == str(svg_file) for f in found_files)
    
    # Check file info
    file_info = next(f for f in found_files if f["path"] == str(svg_file))
    assert file_info["size"] > 0
    assert "modified" in file_info
    assert file_info["has_metadata"] is False
    assert file_info["has_pdf_data"] is False
