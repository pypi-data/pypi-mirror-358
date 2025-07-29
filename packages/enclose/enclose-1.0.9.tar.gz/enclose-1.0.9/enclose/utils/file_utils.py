"""
File system utilities.
"""

from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


def search_svg_files(search_path="."):
    """Search filesystem for SVG files and their metadata."""
    svg_files = []
    search_dir = Path(search_path)

    for svg_file in search_dir.rglob("*.svg"):
        try:
            with open(svg_file, 'r') as f:
                content = f.read()

            # Parse SVG for metadata
            soup = BeautifulSoup(content, 'xml')
            metadata_elem = soup.find('metadata')

            file_info = {
                "path": str(svg_file),
                "size": svg_file.stat().st_size,
                "modified": datetime.fromtimestamp(svg_file.stat().st_mtime).isoformat(),
                "has_metadata": metadata_elem is not None,
                "has_pdf_data": 'data:application/pdf;base64,' in content
            }

            if metadata_elem:
                title_elem = soup.find('dc:title')
                if title_elem:
                    file_info["title"] = title_elem.get_text()

            svg_files.append(file_info)
            print(f"Found SVG: {svg_file}")

        except Exception as e:
            print(f"Error processing {svg_file}: {e}")

    return svg_files
