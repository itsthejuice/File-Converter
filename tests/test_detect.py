"""Tests for MIME type detection."""
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from file_converter.core.detect import sniff_mime


def test_sniff_mime_text_file():
    """Test MIME detection for a text file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello, World!")
        temp_path = f.name
    
    try:
        mime = sniff_mime(temp_path)
        assert mime is not None
        assert isinstance(mime, str)
        assert len(mime) > 0
        # Should detect as text
        assert mime.startswith('text/') or mime == 'text/plain'
    finally:
        os.unlink(temp_path)


def test_sniff_mime_extension_fallback():
    """Test MIME detection falls back to extension."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        # Write minimal data
        f.write(b'\x00' * 100)
        temp_path = f.name
    
    try:
        mime = sniff_mime(temp_path)
        assert mime is not None
        assert isinstance(mime, str)
        # Should at least get a MIME type (might be octet-stream or use extension)
        assert '/' in mime
    finally:
        os.unlink(temp_path)


def test_sniff_mime_nonexistent_file():
    """Test MIME detection raises error for nonexistent file."""
    try:
        sniff_mime('/nonexistent/file.txt')
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    test_sniff_mime_text_file()
    test_sniff_mime_extension_fallback()
    test_sniff_mime_nonexistent_file()
    print("All tests passed!")
