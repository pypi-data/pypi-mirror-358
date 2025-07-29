"""
Document Processing Pipeline
Handles: Markdown → PDF → SVG → PNG → OCR → Search → Aggregation
"""

from .core.document_processor import DocumentProcessor

__all__ = ['DocumentProcessor']
