"""
OCR processing utilities.
"""

import pytesseract
from PIL import Image


def process_ocr(png_files, metadata):
    """Process PNG files with OCR and update metadata."""
    for page_info in png_files:
        try:
            # Perform OCR
            image = Image.open(page_info["file"])
            ocr_text = pytesseract.image_to_string(image)

            # Extract structured data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            page_info["ocr_text"] = ocr_text.strip()
            page_info["ocr_confidence"] = sum(ocr_data['conf']) / len([x for x in ocr_data['conf'] if x > 0])
            page_info["word_count"] = len(ocr_text.split())

            print(f"OCR processed: {page_info['file']}")

        except Exception as e:
            print(f"OCR failed for {page_info['file']}: {e}")
            page_info["ocr_text"] = ""
            page_info["ocr_confidence"] = 0

    metadata["ocr_data"] = png_files
    return metadata
