"""
File validation utilities.
"""
import os
import filetype
from pathlib import Path
from typing import Dict, Tuple, Optional, Union, Any

def get_file_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get the MIME type of a file using filetype.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type as a string (e.g., 'application/pdf')
    """
    try:
        kind = filetype.guess(str(file_path))
        if kind is None:
            # For text files, return text/plain
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Try to read a bit to check if it's text
                return 'text/plain'
            except:
                return 'application/octet-stream'
        return kind.mime
    except Exception as e:
        return f"error: {str(e)}"

def validate_file_signature(file_path: Union[str, Path], expected_type: str) -> Tuple[bool, str]:
    """
    Validate a file's signature against its expected type.
    
    Args:
        file_path: Path to the file
        expected_type: Expected file type ('pdf', 'svg', 'png', 'jpeg', etc.)
        
    Returns:
        Tuple of (is_valid, message)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return False, f"File does not exist: {file_path}"
    
    # Map of expected MIME types for each file extension
    expected_mime_types = {
        'pdf': 'application/pdf',
        'svg': 'image/svg+xml',
        'png': 'image/png',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'html': 'text/html',
        'txt': 'text/plain',
        'md': 'text/markdown'
    }
    
    expected_ext = expected_type.lower()
    expected_mime = expected_mime_types.get(expected_ext)
    
    if not expected_mime:
        return False, f"Unsupported file type for validation: {expected_type}"
    
    # Special handling for text-based formats
    if expected_ext in ['html', 'md', 'txt']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024).lower()
                
                # Check for HTML files
                if expected_ext == 'html' and ('<!doctype html' in content or '<html' in content):
                    return True, f"Valid HTML file: {expected_mime}"
                # Check for Markdown files (simple check for common markdown patterns)
                elif expected_ext == 'md' and any(c in content for c in ['# ', '## ', '* ', '- ']):
                    return True, f"Valid Markdown file: {expected_mime}"
                # For plain text, just check if it's readable
                elif expected_ext == 'txt':
                    return True, f"Valid text file: {expected_mime}"
                    
                return False, f"Invalid {expected_ext.upper()} file: Content doesn't match expected format"
        except Exception as e:
            return False, f"Error reading {expected_ext.upper()} file: {str(e)}"
    
    # Special handling for SVG files since they're XML
    if expected_ext == 'svg':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024).lower()
                if '<!doctype svg' in content or '<svg' in content:
                    return True, "Valid SVG file: image/svg+xml"
                return False, "Invalid SVG file: Missing SVG/XML declaration"
        except Exception as e:
            return False, f"Error reading SVG file: {str(e)}"
    
    # For binary file types, use filetype
    try:
        kind = filetype.guess(str(file_path))
        if kind is None:
            # If filetype can't determine the type, check if it's a valid file
            if file_path.stat().st_size > 0:
                return False, f"Could not determine file type"
            return False, "File is empty"
        
        if kind.mime == expected_mime:
            return True, f"Valid {expected_ext.upper()} file: {kind.mime}"
        else:
            return False, f"Invalid {expected_ext.upper()} file. Expected {expected_mime}, got {kind.mime}"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def validate_converted_file(file_path: Union[str, Path], original_path: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """
    Validate a converted file's MIME type and signature.
    
    Args:
        file_path: Path to the converted file
        original_path: Optional path to the original file for comparison
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'file': str(file_path),
        'exists': os.path.exists(file_path),
        'size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'mime_type': '',
        'is_valid': False,
        'validation_message': ''
    }
    
    if not result['exists']:
        result['validation_message'] = 'File does not exist'
        return result
    
    # Get file extension and validate
    ext = Path(file_path).suffix.lower().lstrip('.')
    if not ext:
        result['validation_message'] = 'No file extension found'
        return result
    
    # Get MIME type
    result['mime_type'] = get_file_mime_type(file_path)
    
    # Validate file signature
    is_valid, message = validate_file_signature(file_path, ext)
    result['is_valid'] = is_valid
    result['validation_message'] = message
    
    # If original file is provided, compare sizes (basic sanity check)
    if original_path and os.path.exists(original_path):
        try:
            orig_size = os.path.getsize(original_path)
            new_size = result['size_bytes']
            result['original_size'] = orig_size
            result['size_ratio'] = new_size / orig_size if orig_size > 0 else 0
        except Exception as e:
            result['size_comparison_error'] = str(e)
    
    return result
