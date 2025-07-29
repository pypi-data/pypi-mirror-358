"""
Tests for the command-line interface.
"""
import pytest
import subprocess
import sys
from pathlib import Path


def test_cli_help(capsys):
    """Test the CLI help message."""
    # This will be used once we have the CLI properly set up
    # For now, we'll just test that the module can be imported
    try:
        import processor.__main__
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import processor.__main__: {e}")


def test_cli_create_command(temp_output_dir, monkeypatch):
    """Test the 'create' command."""
    # Mock command line arguments
    test_args = ["--step", "create", "--output", str(temp_output_dir)]
    
    # Import the main module and run with test arguments
    import processor.__main__ as main
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set test arguments
        sys.argv = ["processor"] + test_args
        
        # Run the main function
        main.main()
        
        # Check if the markdown file was created
        md_file = temp_output_dir / "invoice_example.md"
        assert md_file.exists()
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def test_cli_process_command(temp_output_dir, monkeypatch):
    """Test the 'process' command."""
    # First create an example markdown file
    from processor.converters.markdown_converter import create_example_markdown
    create_example_markdown(temp_output_dir)
    
    # Mock command line arguments
    test_args = ["--step", "process", "--output", str(temp_output_dir)]
    
    # Import the main module
    import processor.__main__ as main
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set test arguments
        sys.argv = ["processor"] + test_args
        
        # Run the main function
        main.main()
        
        # Check if output files were created
        assert (temp_output_dir / "invoice_example.pdf").exists()
        assert (temp_output_dir / "invoice_example.svg").exists()
        assert any(temp_output_dir.glob("page_*.png"))
        assert (temp_output_dir / "metadata.json").exists()
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv
