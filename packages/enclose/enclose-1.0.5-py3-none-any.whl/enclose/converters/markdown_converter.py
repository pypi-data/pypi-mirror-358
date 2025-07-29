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
    with open(file_path, 'w') as f:
        f.write(markdown_content)

    print(f"Created: {file_path}")
    return file_path


def markdown_to_html(md_file, output_dir, output_file=None):
    """Convert markdown to HTML.

    Args:
        md_file: Path or string to the input markdown file
        output_dir: Directory to save the output HTML
        output_file: Optional output filename (without extension)

    Returns:
        Path to the generated HTML file
    """
    # Handle both string paths and Path objects
    md_path = Path(md_file) if not isinstance(md_file, Path) else md_file
    output_dir = Path(output_dir)

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    extensions = ['tables', 'fenced_code', 'codehilite']
    html_content = markdown.markdown(md_content, extensions=extensions)
    
    # Add CSS styling for better HTML output
    styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
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
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            display: block;
            overflow-x: auto;
        }}
        th, td {{
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f6f8fa;
        }}
        code {{
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            padding: 0.2em 0.4em;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            font-size: 85%;
            line-height: 1.45;
        }}
        blockquote {{
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            margin: 0 0 16px 0;
            padding: 0 1em;
        }}
        img {{
            max-width: 100%;
            box-sizing: border-box;
            display: block;
            margin: 0 auto;
        }}
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #0d1117;
                color: #c9d1d9;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #e6edf3;
                border-color: #30363d;
            }}
            a {{
                color: #58a6ff;
            }}
            code, pre {{
                background-color: rgba(110, 118, 129, 0.4);
            }}
            th, tr:nth-child(even) {{
                background-color: #161b22;
            }}
            td, th {{
                border-color: #30363d;
            }}
            blockquote {{
                color: #8b949e;
                border-color: #30363d;
            }}
        }}
    </style>
</head>
<body>
    <article class="markdown-body">
        {html_content}
    </article>
</body>
</html>
"""

    # Generate output path
    if output_file is None:
        output_file = md_path.stem
    html_path = output_dir / f"{output_file}.html"

    # Write HTML to file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html.strip())

    print(f"Created: {html_path}")
    return html_path


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
