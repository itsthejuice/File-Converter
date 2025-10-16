"""MIME type detection utilities."""
import magic
import os
from pathlib import Path


# Extension fallback mapping
EXTENSION_FALLBACK = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mkv': 'video/x-matroska',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.mp3': 'audio/mpeg',
    '.flac': 'audio/flac',
    '.wav': 'audio/wav',
    '.ogg': 'audio/ogg',
    '.gif': 'image/gif',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.html': 'text/html',
    '.htm': 'text/html',
}

# Supported MIME types (will be populated by registry)
_supported_mimes = set()


def sniff_mime(path: str) -> str:
    """
    Detect MIME type of a file using python-magic with extension fallback.
    
    Args:
        path: Path to the file
        
    Returns:
        MIME type string
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Try python-magic first
    try:
        mime = magic.from_file(str(path), mime=True)
        if mime and mime != 'application/octet-stream':
            return mime
    except Exception:
        pass
    
    # Fall back to extension
    ext = path.suffix.lower()
    if ext in EXTENSION_FALLBACK:
        return EXTENSION_FALLBACK[ext]
    
    # Last resort
    return 'application/octet-stream'


def is_supported(mime: str) -> bool:
    """
    Check if a MIME type is supported by any loaded plugin.
    
    Args:
        mime: MIME type string
        
    Returns:
        True if supported
    """
    return mime in _supported_mimes


def register_supported_mime(mime: str) -> None:
    """Register a MIME type as supported."""
    _supported_mimes.add(mime)


def clear_supported_mimes() -> None:
    """Clear the supported MIME types (for testing)."""
    _supported_mimes.clear()
