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


def markdown_to_pdf(md_file, output_dir):
    """Convert markdown to PDF."""
    with open(md_file, 'r') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables'])

    # Add CSS styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1, h2 {{ color: #333; }}
        </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    pdf_path = output_dir / "invoice_example.pdf"
    HTML(string=styled_html).write_pdf(pdf_path)

    print(f"Created: {pdf_path}")
    return pdf_path
