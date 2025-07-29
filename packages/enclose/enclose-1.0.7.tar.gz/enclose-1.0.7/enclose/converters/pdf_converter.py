"""PDF conversion utilities."""

import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from PIL import Image
from typing_extensions import TypedDict

# cairosvg doesn't have type stubs
import cairosvg  # type: ignore[import-untyped]


def pdf_to_svg(
    pdf_file: Union[str, Path],
    output_dir: Union[str, Path],
) -> Tuple[Path, Dict[str, Any]]:
    """Convert PDF to SVG with embedded data and metadata.

    Args:
        pdf_file: Path or string to the input PDF file
        output_dir: Directory to save the output SVG

    Returns:
        Tuple of (output_svg_path, metadata_dict)
    """
    # Convert to Path objects if they are strings
    pdf_path = Path(pdf_file) if isinstance(pdf_file, str) else pdf_file
    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output path
    output_path = output_dir / f"{pdf_path.stem}.svg"
    
    # Read PDF as base64
    with open(pdf_file, 'rb') as f:
        pdf_data = base64.b64encode(f.read()).decode('utf-8')

    # Create metadata
    metadata = {
        "file": str(output_path),
        "pdf_embedded": True,
        "pages": [],
        "total_pages": 1  # Default to 1 page, can be updated if we have page count
    }
    
    # Create SVG with embedded PDF data
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="800" height="1000" viewBox="0 0 800 1000">

    <!-- Metadata -->
    <metadata>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:Description rdf:about="">
                <dc:title>PDF Document</dc:title>
                <dc:creator>Enclose Document Processor</dc:creator>
                <dc:date>{datetime.now().isoformat()}</dc:date>
                <dc:description>PDF embedded in SVG container</dc:description>
            </rdf:Description>
        </rdf:RDF>
    </metadata>

    <!-- Background -->
    <rect width="100%" height="100%" fill="white"/>

    <!-- PDF Data (base64 encoded) -->
    <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">
            <embed src="data:application/pdf;base64,{pdf_data}"
                   width="100%" height="100%" type="application/pdf"/>
        </div>
    </foreignObject>

    <!-- Visual representation -->
    <text x="50" y="50" font-family="Arial" font-size="24" fill="black">
        PDF Document
    </text>
    <rect x="50" y="70" width="700" height="2" fill="#333"/>
    <text x="50" y="120" font-family="Arial" font-size="16" fill="gray">
        PDF content embedded as data URI
    </text>
</svg>"""

    # Write SVG to file
    output_path.write_text(svg_content, encoding='utf-8')
    print(f"Created: {output_path}")
    return output_path, metadata


class PageInfo(TypedDict):
    page: int
    file: str
    width: int
    height: int


def svg_to_png(
    svg_file: Union[str, Path],
    metadata: Dict[str, Any],
    output_dir: Union[str, Path],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Convert SVG to PNG images.

    Args:
        svg_file: Path or string to the input SVG file
        metadata: Metadata from the PDF to SVG conversion
        output_dir: Directory to save the output PNG files

    Returns:
        Tuple of (list of page info dicts, updated metadata)
    """
    # Convert to Path objects if they are strings
    svg_file = Path(svg_file) if isinstance(svg_file, str) else svg_file
    output_dir = Path(output_dir) if isinstance(
        output_dir, str
    ) else output_dir

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Create output filename
        output_path = output_dir / f"{svg_file.stem}.png"
        svg_path = str(svg_file.absolute())

        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(url=svg_path)

        # Save the PNG data to a file and get dimensions
        with open(output_path, 'wb') as f:
            f.write(png_data)
        with Image.open(io.BytesIO(png_data)) as img:
            width, height = img.size

        # Create and update page info
        page_info = [
            {
                "page": 1,
                "file": str(output_path.absolute()),
                "width": width,
                "height": height,
            },
        ]
        metadata.update(
            {
                "pages": page_info,
                "converted_at": datetime.now().isoformat(),
            }
        )

        print(f"Created: {output_path}")
        return page_info, metadata

    except Exception as e:
        raise RuntimeError(f"Failed to convert SVG to PNG: {str(e)}")
