"""
Tests for markdown_converter module.
"""
import pytest
from pathlib import Path
from processor.converters.markdown_converter import create_example_markdown, markdown_to_pdf


def test_create_example_markdown(temp_output_dir):
    """Test creating an example markdown file."""
    # Create the markdown file in the temp directory
    md_file = create_example_markdown(temp_output_dir)
    
    # Check if file was created
    assert md_file.exists()
    assert md_file.name == "invoice_example.md"
    
    # Check file content
    content = md_file.read_text()
    assert "# Invoice Example" in content
    assert "## Invoice #INV-2025-001" in content


def test_markdown_to_pdf(example_markdown_file, temp_output_dir):
    """Test converting markdown to PDF."""
    # Convert markdown to PDF
    pdf_file = markdown_to_pdf(example_markdown_file, temp_output_dir)
    
    # Check if PDF was created
    assert pdf_file.exists()
    assert pdf_file.suffix == ".pdf"
    assert pdf_file.stat().st_size > 0  # File is not empty
