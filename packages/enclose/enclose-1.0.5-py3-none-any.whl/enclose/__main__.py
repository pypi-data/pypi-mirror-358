#!/usr/bin/env python3
"""
Main entry point for the enclose command-line interface.

This module provides the command-line interface for the enclose document
processing tool.
"""

import argparse
import sys
from typing import Optional

from .core.document_processor import DocumentProcessor


def list_formats() -> None:
    """List all supported formats and conversions."""
    processor = DocumentProcessor()
    formats = processor.get_supported_formats()

    print("\nSupported formats:")
    print(f"Input formats: {', '.join(formats['input_formats'])}")
    print(f"Output formats: {', '.join(formats['output_formats'])}")

    print("\nSupported conversions:")
    for src, dests in formats["conversions"].items():
        print(f"{src.upper()} -> {', '.join(dests).upper()}")


def convert_file(
    input_path: str,
    output_format: str,
    output_path: Optional[str] = None
) -> None:
    """Convert a file to the specified format.
    
    Args:
        input_path: Path to the input file
        output_format: Desired output format
        output_path: Optional output file path
    """
    processor = DocumentProcessor()
    try:
        result = processor.process(input_path, output_format, output_path)
        print(f"Successfully created: {result}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Document Processing Pipeline - Convert between formats"
    )
    
    # Add --version flag
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0',
        help='Show version and exit',
    )

    # Add --list flag
    parser.add_argument(
        '--list',
        action='store_true',
        help='List supported formats and exit',
    )

    # Positional arguments
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file to process (required for conversion)',
    )

    parser.add_argument(
        'output_format',
        nargs='?',
        choices=['pdf', 'png', 'svg', 'html'],
        help='Output format (required for conversion)',
    )

    # Optional output file
    parser.add_argument(
        '-o',
        '--output',
        help='Output file path (default: auto-generated)',
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    
    if args.list:
        list_formats()
        return
    
    if not args.input or not args.output_format:
        print("Error: Both input file and output format are required")
        print("Use 'enclose --help' for usage information")
        sys.exit(1)
    
    convert_file(args.input, args.output_format, args.output)


if __name__ == "__main__":
    main()
