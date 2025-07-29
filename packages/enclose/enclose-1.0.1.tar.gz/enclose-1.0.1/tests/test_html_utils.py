"""
Tests for html_utils module.
"""
import pytest
from pathlib import Path
from processor.utils.html_utils import aggregate_to_html_table


def test_aggregate_to_html_table(temp_output_dir):
    """Test HTML table generation with SVG thumbnails."""
    # Create test SVG files data
    svg_files_data = [
        {
            "path": str(temp_output_dir / "test1.svg"),
            "size": 1024,
            "modified": "2025-01-01T12:00:00",
            "has_metadata": True,
            "has_pdf_data": True,
            "title": "Test Document 1"
        },
        {
            "path": str(temp_output_dir / "test2.svg"),
            "size": 2048,
            "modified": "2025-01-02T12:00:00",
            "has_metadata": False,
            "has_pdf_data": False,
            "title": "Test Document 2"
        }
    ]
    
    # Create actual SVG files to be embedded
    for svg_data in svg_files_data:
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" fill="#f0f0f0"/>
            <text x="10" y="30" font-family="Arial" font-size="12">{svg_data['title']}</text>
        </svg>"""
        Path(svg_data["path"]).write_text(svg_content)
    
    # Generate HTML table
    html_path = temp_output_dir / "dashboard.html"
    result_path = aggregate_to_html_table(svg_files_data, html_path)
    
    # Check if HTML file was created
    assert result_path == html_path
    assert html_path.exists()
    assert html_path.stat().size > 0
    
    # Check HTML content
    content = html_path.read_text()
    assert "<title>SVG Files Dashboard</title>" in content
    assert "<table>" in content
    
    # Check if both test files are in the table
    for svg_data in svg_files_data:
        assert svg_data["path"] in content
        assert svg_data["title"] in content
