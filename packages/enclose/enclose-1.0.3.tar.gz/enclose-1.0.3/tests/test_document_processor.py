"""
Tests for the DocumentProcessor class.
"""
import pytest
from pathlib import Path
from processor.core.document_processor import DocumentProcessor


def test_document_processor_init(temp_output_dir):
    """Test DocumentProcessor initialization."""
    # Test with custom output directory
    processor = DocumentProcessor(str(temp_output_dir))
    assert processor.output_dir == temp_output_dir
    assert temp_output_dir.exists()
    assert isinstance(processor.metadata, dict)
    assert not processor.metadata  # Should be empty initially


def test_create_example_markdown(temp_output_dir):
    """Test creating an example markdown file."""
    processor = DocumentProcessor(temp_output_dir)
    md_file = processor.create_example_markdown()
    
    # Check if file was created
    assert md_file.exists()
    assert md_file.name == "invoice_example.md"
    
    # Check file content
    content = md_file.read_text()
    assert "# Invoice Example" in content


def test_full_processing_pipeline(example_markdown_file, temp_output_dir):
    """Test the full document processing pipeline."""
    processor = DocumentProcessor(temp_output_dir)
    
    # Step 1: Create example markdown (or use provided one)
    md_file = example_markdown_file
    
    # Step 2: Convert markdown to PDF
    pdf_file = processor.markdown_to_pdf(md_file)
    assert pdf_file.exists()
    
    # Step 3: Convert PDF to SVG
    svg_file, metadata1 = processor.pdf_to_svg(pdf_file)
    assert svg_file.exists()
    assert "file" in metadata1
    assert metadata1["file"] == str(svg_file)
    
    # Step 4: Convert SVG to PNG
    png_files, metadata2 = processor.svg_to_png(svg_file, metadata1)
    assert len(png_files) > 0
    assert "pages" in metadata2
    assert len(metadata2["pages"]) > 0
    
    # Step 5: Process OCR
    metadata3 = processor.process_ocr(png_files, metadata2)
    assert "ocr_data" in metadata3
    assert len(metadata3["ocr_data"]) > 0
    
    # Step 6: Search for SVG files
    svg_files = processor.search_svg_files(temp_output_dir)
    assert len(svg_files) > 0
    
    # Step 7: Create HTML dashboard
    html_path = processor.enclose_to_html_table(svg_files)
    assert html_path.exists()
    
    # Save metadata
    metadata_path = processor.save_metadata(metadata3, "final_metadata.json")
    assert metadata_path.exists()
