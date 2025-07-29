"""
HTML generation utilities.
"""

import webbrowser
from pathlib import Path


def enclose_to_html_table(svg_files_data, html_path):
    """
    Create an HTML table with SVG thumbnails.
    
    Args:
        svg_files_data: List of dictionaries containing SVG file metadata
        html_path: Path where the HTML file should be saved (can be a directory or file path)
        
    Returns:
        Path to the generated HTML file
    """
    # Convert to Path object if it's a string
    html_path = Path(html_path)
    
    # If the path is a directory, create the default filename
    if html_path.is_dir() or not html_path.suffix == '.html':
        html_path = html_path / "dashboard.html"
    
    # Create parent directories if they don't exist
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>SVG Files Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .thumbnail { width: 200px; height: 150px; border: 1px solid #ccc; }
        .metadata { font-size: 12px; color: #666; }
        .svg-preview { max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>
    <h1>SVG Files Dashboard</h1>
    <table>
        <thead>
            <tr>
                <th>Thumbnail</th>
                <th>File Path</th>
                <th>Size</th>
                <th>Modified</th>
                <th>Has PDF</th>
                <th>Metadata</th>
            </tr>
        </thead>
        <tbody>
"""

    for svg_data in svg_files_data:
        # Create thumbnail
        thumbnail_html = '<div class="thumbnail">SVG Preview</div>'
        
        # Skip if svg_data is not a dictionary or doesn't have a path
        if not isinstance(svg_data, dict) or "path" not in svg_data:
            continue
            
        try:
            svg_path = Path(svg_data["path"])
            if svg_path.exists() and svg_path.is_file():
                with open(svg_path, 'r') as f:
                    svg_content = f.read()
                # Embed SVG directly as thumbnail
                thumbnail_html = f'<div class="thumbnail">{svg_content}</div>'
        except Exception as e:
            print(f"Warning: Could not read SVG file {svg_data.get('path', 'unknown')}: {str(e)}")
            continue

        has_pdf = "✓" if svg_data.get("has_pdf_data") else "✗"
        has_metadata = "✓" if svg_data.get("has_metadata") else "✗"
        title = svg_data.get("title", "No title")
        file_size = svg_data.get("size", "N/A")
        modified = svg_data.get("modified", "N/A")

        html_content += f"""
        <tr>
            <td>{thumbnail_html}</td>
            <td><a href="file://{svg_path.absolute()}">{svg_path.name}</a></td>
            <td>{file_size}</td>
            <td>{modified}</td>
            <td>{has_pdf}</td>
            <td class="metadata">
                Metadata: {has_metadata}<br>
                Title: {title}
            </td>
        </tr>
        """

    html_content += """
        </tbody>
    </table>
</body>
</html>
"""

    # Write the HTML content to file
    try:
        with open(html_path, 'w') as f:
            f.write(html_content)
        print(f"Created dashboard: {html_path.absolute()}")
        
        # Try to open in browser
        try:
            webbrowser.open(f"file://{html_path.absolute()}")
        except Exception as e:
            print(f"Note: Could not open browser: {str(e)}")
            
    except Exception as e:
        print(f"Error: Could not write to {html_path}: {str(e)}")
        raise
        
    return html_path
