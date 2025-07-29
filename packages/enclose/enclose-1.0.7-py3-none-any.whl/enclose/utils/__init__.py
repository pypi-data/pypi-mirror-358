"""
Utility functions for the document processing pipeline.
"""

from .ocr_processor import process_ocr
from .file_utils import search_svg_files
from .html_utils import enclose_to_html_table
from .metadata_utils import save_metadata
from .file_validation import (
    get_file_mime_type,
    validate_file_signature,
    validate_converted_file
)

__all__ = [
    'process_ocr',
    'search_svg_files',
    'enclose_to_html_table',
    'save_metadata',
    'get_file_mime_type',
    'validate_file_signature',
    'validate_converted_file',
]
