"""
HTML generation utilities.
"""

import os
import webbrowser
from pathlib import Path


def enclose_to_html_table(svg_files_data, html_path):
    """Create HTML table with SVG thumbnails."""
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
        if os.path.exists(svg_data["path"]):
            try:
                with open(svg_data["path"], 'r') as f:
                    svg_content = f.read()
                # Embed SVG directly as thumbnail
                thumbnail_html = f'<div class="thumbnail">{svg_content}</div>'
            except Exception:
                pass

        has_pdf = "✓" if svg_data.get("has_pdf_data") else "✗"
        has_metadata = "✓" if svg_data.get("has_metadata") else "✗"
        title = svg_data.get("title", "No title")

        html_content += f"""
        <tr>
            <td>{thumbnail_html}</td>
            <td><a href="file://{svg_data['path']}">{svg_data['path']}</a></td>
            <td>{svg_data['size']} bytes</td>
            <td>{svg_data['modified']}</td>
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

    with open(html_path, 'w') as f:
        f.write(html_content)

    print(f"Created dashboard: {html_path}")

    # Open in browser
    webbrowser.open(f"file://{html_path.absolute()}")

    return html_path
