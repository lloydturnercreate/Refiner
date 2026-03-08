"""
Utility helpers for file extensions, sizes, and validation.
"""

import os
import math
from typing import Optional
from constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AVAILABLE_FORMATS


def normalize_extension(ext: str) -> str:
    """Return a normalized, lowercase extension with leading dot (e.g. '.jpg')."""
    ext = ext.lower()
    if not ext.startswith('.'):
        ext = f'.{ext}'
    
    # Unify .jpeg to .jpg for consistency
    if ext == '.jpeg':
        return '.jpg'
    return ext


def convert_size(size_bytes: int) -> str:
    """Convert byte count to a human-readable string (e.g. '1.5MB')."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{size_names[i]}"


def get_file_type(file_path: str) -> str:
    """Return 'image', 'video', or 'unknown' based on the file extension."""
    ext = normalize_extension(os.path.splitext(file_path)[1])
    
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    elif ext in VIDEO_EXTENSIONS:
        return 'video'
    else:
        return 'unknown'


def is_supported_format(file_path: str) -> bool:
    """Return True if the file extension is among supported formats."""
    ext = normalize_extension(os.path.splitext(file_path)[1])
    return ext in AVAILABLE_FORMATS


def get_valid_output_formats(input_path: str) -> list:
    """Return a list of valid output extensions for the given input file."""
    input_ext = normalize_extension(os.path.splitext(input_path)[1])
    
    if input_ext in IMAGE_EXTENSIONS:
        return [ext for ext in IMAGE_EXTENSIONS if ext != input_ext]
    elif input_ext in VIDEO_EXTENSIONS:
        return [ext for ext in VIDEO_EXTENSIONS if ext != input_ext]
    else:
        return AVAILABLE_FORMATS


def generate_output_filename(input_path: str, suffix: str = "-min") -> str:
    """Return input filename with suffix inserted before the extension."""
    base, ext = os.path.splitext(input_path)
    return f"{base}{suffix}{ext}"


def validate_file_path(file_path: str) -> tuple[bool, Optional[str]]:
    """Validate path existence and readability; returns (is_valid, error_message)."""
    if not file_path:
        return False, "No file path provided"
    
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not os.path.isfile(file_path):
        return False, "Path is not a file"
    
    if not os.access(file_path, os.R_OK):
        return False, "File is not readable"
    
    return True, None
