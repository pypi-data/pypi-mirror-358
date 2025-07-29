"""
Markdown conversion utilities.
"""

from pathlib import Path
import markdown
from weasyprint import HTML


def create_example_markdown(output_dir):
    """Create an example markdown file."""
    markdown_content = """# Invoice Example

## Invoice #INV-2025-001

**Date:** June 25, 2025  
**Due Date:** July 25, 2025

### Bill To:
**Customer Name:** John Smith  
**Address:** 123 Main Street  
**City:** New York, NY 10001

### Services Provided:

| Item | Description | Quantity | Rate | Amount |
|------|-------------|----------|------|--------|
| 1 | Web Development | 40 hrs | $100/hr | $4,000 |
| 2 | Design Services | 20 hrs | $80/hr | $1,600 |
| 3 | Consultation | 10 hrs | $120/hr | $1,200 |

### Summary:
- **Subtotal:** $6,800
- **Tax (8.5%):** $578
- **Total:** $7,378

### Payment Terms:
Payment is due within 30 days of invoice date.

### Notes:
Thank you for your business!
"""

    file_path = output_dir / "invoice_example.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Created: {file_path}")
    return file_path


def markdown_to_html(md_file, output_dir, output_file=None):
    """Convert markdown to HTML.

    Args:
        md_file: Path or string to the input markdown file
        output_dir: Directory to save the output HTML
        output_file: Optional output filename (with or without .html extension)

    Returns:
        Path to the generated HTML file
    """
    # Handle both string paths and Path objects
    md_path = Path(md_file) if not isinstance(md_file, Path) else md_file
    output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set output filename
    if output_file is None:
        output_file = f"{md_path.stem}.html"
    elif not str(output_file).lower().endswith('.html'):
        output_file = f"{output_file}.html"
    
    output_path = output_dir / output_file

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    extensions = ['tables', 'fenced_code', 'codehilite']
    html_content = markdown.markdown(md_content, extensions=extensions)
    
    # Add CSS styling for better HTML output
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                      Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #24292e;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        h5 {{ font-size: 0.875em; }}
        h6 {{ font-size: 0.85em; color: #6a737d; }}
        p, ul, ol, dl, table, pre, blockquote {{
            margin-top: 0;
            margin-bottom: 16px;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code, pre {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
        }}
        pre {{
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 3px;
        }}
        pre > code {{
            background-color: transparent;
            padding: 0;
            margin: 0;
            font-size: 100%;
            word-break: normal;
            white-space: pre;
            border: 0;
        }}
        img {{ max-width: 100%; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
            display: block;
            overflow: auto;
        }}
        th, td {{
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }}
        tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}
        blockquote {{
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
            margin: 0 0 16px 0;
        }}
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    # Write the HTML content to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    return output_path


def markdown_to_pdf(md_file, output_dir, output_file=None):
    """Convert markdown to PDF.

    Args:
        md_file: Path or string to the input markdown file
        output_dir: Directory to save the output PDF
        output_file: Optional output filename (without extension)

    Returns:
        Path to the generated PDF file
    """
    # First convert to HTML
    html_path = markdown_to_html(md_file, output_dir, output_file)

    # Generate PDF path
    if output_file is None:
        output_file = Path(md_file).stem
    pdf_path = Path(output_dir) / f"{output_file}.pdf"

    # Convert HTML to PDF
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))

    # Clean up the temporary HTML file if it's different from the output file
    if html_path != pdf_path.with_suffix('.html'):
        html_path.unlink()

    print(f"Created: {pdf_path}")
    return pdf_path
