"""
Utility functions for Cloudflare Images Migration Tool
"""

import os
import re
import shutil
import zipfile
import tempfile
import hashlib
import validators
from pathlib import Path
from typing import List, Optional, Tuple, Set
from urllib.parse import urlparse, urljoin


def validate_path(path: str) -> Path:
    """
    Validate and normalize a file or directory path.
    
    Args:
        path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path is invalid
    """
    path_obj = Path(path).resolve()
    
    if not path_obj.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    return path_obj


def is_zip_file(path: Path) -> bool:
    """Check if a file is a valid zip archive."""
    try:
        with zipfile.ZipFile(path, 'r') as zip_file:
            zip_file.testzip()
        return True
    except (zipfile.BadZipFile, FileNotFoundError):
        return False


def extract_zip(zip_path: Path, extract_to: Optional[Path] = None) -> Path:
    """
    Extract a zip file to a temporary or specified directory.
    
    Args:
        zip_path: Path to zip file
        extract_to: Directory to extract to (optional)
        
    Returns:
        Path to extracted directory
    """
    if extract_to is None:
        extract_to = Path(tempfile.mkdtemp(prefix="cf_images_"))
    
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(extract_to)
    
    return extract_to


def create_backup(source_path: Path, backup_suffix: str = "_backup") -> Path:
    """
    Create a backup of the source directory or file.
    
    Args:
        source_path: Path to backup
        backup_suffix: Suffix to add to backup name
        
    Returns:
        Path to backup
    """
    backup_path = source_path.parent / f"{source_path.name}{backup_suffix}"
    
    # Ensure unique backup name
    counter = 1
    while backup_path.exists():
        backup_path = source_path.parent / f"{source_path.name}{backup_suffix}_{counter}"
        counter += 1
    
    if source_path.is_dir():
        shutil.copytree(source_path, backup_path)
    else:
        shutil.copy2(source_path, backup_path)
    
    return backup_path


def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MD5 hash as hex string
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def is_image_file(file_path: Path, supported_formats: List[str]) -> bool:
    """
    Check if a file is an image based on its extension.
    
    Args:
        file_path: Path to file
        supported_formats: List of supported image extensions
        
    Returns:
        True if file is an image
    """
    return file_path.suffix.lower() in [fmt.lower() for fmt in supported_formats]


def is_url(string: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        string: String to check
        
    Returns:
        True if string is a valid URL
    """
    return validators.url(string) is True


def normalize_path(path: str, base_path: Path = None) -> str:
    """
    Normalize a file path for consistent handling.
    
    Args:
        path: Path to normalize
        base_path: Base path for relative paths
        
    Returns:
        Normalized path string
    """
    if is_url(path):
        return path
    
    # Remove quotes and whitespace
    path = path.strip().strip('"\'')
    
    # Handle relative paths
    if base_path and not os.path.isabs(path):
        normalized = str((base_path / path).resolve())
    else:
        normalized = str(Path(path).resolve())
    
    return normalized


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """
    Get relative path from base path to file path.
    
    Args:
        file_path: Target file path
        base_path: Base directory path
        
    Returns:
        Relative path string
    """
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)


def find_files_by_extension(directory: Path, extensions: List[str], 
                          exclude_dirs: List[str] = None) -> List[Path]:
    """
    Find all files with specified extensions in a directory tree.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions to match
        exclude_dirs: List of directory names to exclude
        
    Returns:
        List of matching file paths
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    exclude_dirs = [d.lower() for d in exclude_dirs]
    extensions = [ext.lower() for ext in extensions]
    
    found_files = []
    
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs list to skip them
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in extensions:
                found_files.append(file_path)
    
    return found_files


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def make_cloudflare_url(image_id: str, variant: str = "public") -> str:
    """
    Generate Cloudflare Images delivery URL.
    
    Args:
        image_id: Cloudflare image ID
        variant: Image variant name
        
    Returns:
        Cloudflare delivery URL
    """
    return f"https://imagedelivery.net/{image_id}/{variant}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe use across different file systems.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary (non-text).
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True  # Assume binary if can't read


def safe_read_file(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read a text file with fallback encodings.
    
    Args:
        file_path: Path to file
        encoding: Primary encoding to try
        
    Returns:
        File content or None if reading fails
    """
    encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            break
    
    return None


def safe_write_file(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to a file.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: Encoding to use
        
    Returns:
        True if successful
    """
    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False 