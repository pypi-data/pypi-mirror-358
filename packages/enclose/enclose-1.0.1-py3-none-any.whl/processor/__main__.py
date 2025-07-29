#!/usr/bin/env python3
"""
Document Processing Pipeline CLI
"""

import argparse
from pathlib import Path

from .core.document_processor import DocumentProcessor


def main():
    parser = argparse.ArgumentParser(description="Document Processing Pipeline")
    parser.add_argument("--step", choices=["create", "process", "enclose", "search"],
                       required=True, help="Processing step to execute")
    parser.add_argument("--output", default="output", help="Output directory")

    args = parser.parse_args()

    processor = DocumentProcessor(args.output)

    if args.step == "create":
        # Step 1: Create example
        processor.create_example_markdown()

    elif args.step == "process":
        # Steps 2-5: Full processing pipeline
        md_file = processor.output_dir / "invoice_example.md"
        if not md_file.exists():
            md_file = processor.create_example_markdown()

        pdf_file = processor.markdown_to_pdf(md_file)
        svg_file, metadata = processor.pdf_to_svg(pdf_file)
        png_files, metadata = processor.svg_to_png(svg_file, metadata)
        metadata = processor.process_ocr(png_files, metadata)
        processor.save_metadata(metadata)

    elif args.step == "search":
        # Step 6: Search for SVG files
        svg_files = processor.search_svg_files()
        processor.save_metadata(svg_files, "svg_search_results.json")

    elif args.step == "enclose":
        # Step 7: Create dashboard
        svg_files = processor.search_svg_files()
        processor.enclose_to_html_table(svg_files)


if __name__ == "__main__":
    main()
