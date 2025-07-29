"""
Tests for metadata_utils module.
"""
import json
from pathlib import Path
from processor.utils.metadata_utils import save_metadata


def test_save_metadata(temp_output_dir):
    """Test saving metadata to a JSON file."""
    # Test metadata
    test_metadata = {
        "file": "test.pdf",
        "type": "test",
        "pages": [1, 2, 3],
        "metadata": {
            "author": "Test User",
            "created": "2025-01-01T00:00:00"
        }
    }
    
    # Save metadata
    output_file = "test_metadata.json"
    result_path = save_metadata(test_metadata, temp_output_dir, output_file)
    
    # Check if file was created
    assert result_path == temp_output_dir / output_file
    assert result_path.exists()
    
    # Check file content
    with open(result_path, 'r') as f:
        loaded_metadata = json.load(f)
    
    assert loaded_metadata == test_metadata
