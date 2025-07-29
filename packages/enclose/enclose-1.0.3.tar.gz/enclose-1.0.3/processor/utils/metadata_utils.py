"""
Metadata handling utilities.
"""

import json
from pathlib import Path


def save_metadata(metadata, output_dir, filename="metadata.json"):
    """Save metadata to JSON file."""
    json_path = output_dir / filename
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata: {json_path}")
    return json_path
