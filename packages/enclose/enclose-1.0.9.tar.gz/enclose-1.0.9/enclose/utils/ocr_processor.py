"""
OCR processing utilities.
"""

import json
import pytesseract
from pathlib import Path
from PIL import Image


def process_ocr(png_files, metadata):
    """Process PNG files with OCR and update metadata.
    
    Args:
        png_files: List of file paths or file objects to process
        metadata: Dictionary containing metadata to update
        
    Returns:
        Updated metadata with OCR results
    """
    if not isinstance(png_files, (list, tuple)):
        png_files = [png_files]
        
    ocr_results = []
    
    for i, page_info in enumerate(png_files):
        result = {"page": i + 1, "ocr_text": "", "ocr_confidence": 0, "word_count": 0}
        
        try:
            # Handle both string paths and file objects
            if isinstance(page_info, (str, Path)):
                file_path = str(page_info)
                image = Image.open(file_path)
                result["file"] = file_path
            elif isinstance(page_info, dict) and "file" in page_info:
                file_path = str(page_info["file"])
                image = Image.open(file_path)
                result.update(page_info)
            else:
                raise ValueError(f"Unsupported page info type: {type(page_info)}")
                
            # Perform OCR
            ocr_text = pytesseract.image_to_string(image)
            
            # Extract structured data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate confidence (handle division by zero)
            confidences = [float(x) for x in ocr_data['conf'] if float(x) > 0]
            confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Update results
            result.update({
                "ocr_text": ocr_text.strip(),
                "ocr_confidence": confidence,
                "word_count": len(ocr_text.split())
            })
            
            print(f"OCR processed: {file_path} (confidence: {confidence:.2f}%)")
            
        except Exception as e:
            error_msg = str(e)
            print(f"OCR failed for page {i+1}: {error_msg}")
            if "file" not in result:
                result["file"] = f"page_{i+1}.png"
            result["error"] = error_msg
            
        ocr_results.append(result)
    
    # Update metadata with OCR results using the expected key 'ocr_data'
    metadata["ocr_data"] = ocr_results
    return metadata
