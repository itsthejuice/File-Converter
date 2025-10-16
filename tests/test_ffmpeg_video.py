"""Tests for FFmpeg video plugin."""
import tempfile
import os
import shutil
import subprocess
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from file_converter.core.registry import Registry
from file_converter.core.jobs import Job, Status
from file_converter.core.engine import plan_and_run
from file_converter.core.presets import load_defaults


def has_ffmpeg():
    """Check if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None


def create_test_audio_file(output_path):
    """Create a small test audio file using ffmpeg."""
    if not has_ffmpeg():
        return False
    
    try:
        # Generate 1 second of silence
        subprocess.run(
            [
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "1", "-y", str(output_path)
            ],
            capture_output=True,
            timeout=10,
            check=True
        )
        return True
    except Exception:
        return False


def test_ffmpeg_plugin_available():
    """Test that FFmpeg plugin loads and is available."""
    if not has_ffmpeg():
        print("SKIP: ffmpeg not available")
        return
    
    registry = Registry()
    plugin_dir = Path(__file__).parent.parent / "src" / "file_converter" / "plugins"
    registry.load_plugins(plugin_dir)
    
    available = registry.get_available_plugins()
    assert len(available) > 0, "No plugins available"
    
    ffmpeg_plugin = next((p for p in available if p.name == "ffmpeg_video"), None)
    assert ffmpeg_plugin is not None, "FFmpeg plugin not found"
    
    print("✓ FFmpeg plugin is available")


def test_conversion_wav_to_mp3():
    """Test WAV to MP3 conversion."""
    if not has_ffmpeg():
        print("SKIP: ffmpeg not available")
        return
    
    # Create test file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        input_file = tmpdir / "test_input.wav"
        
        if not create_test_audio_file(input_file):
            print("SKIP: Could not create test file")
            return
        
        assert input_file.exists(), "Test file was not created"
        
        # Set up conversion
        registry = Registry()
        plugin_dir = Path(__file__).parent.parent / "src" / "file_converter" / "plugins"
        registry.load_plugins(plugin_dir)
        
        presets = load_defaults()
        
        job = Job(
            id="test-1",
            src_path=str(input_file),
            src_mime="audio/wav",
            dst_mime="audio/mp3",
            options={"quality": 2}
        )
        
        # Run conversion
        result = plan_and_run(job, registry, presets, str(tmpdir))
        
        # Verify results
        assert result.status == Status.DONE.value, f"Conversion failed: {result.logs}"
        assert result.output_path is not None, "No output path"
        
        output_file = Path(result.output_path)
        assert output_file.exists(), "Output file does not exist"
        assert output_file.stat().st_size > 0, "Output file is empty"
        
        print(f"✓ Conversion successful: {output_file.name} ({output_file.stat().st_size} bytes)")


if __name__ == "__main__":
    test_ffmpeg_plugin_available()
    test_conversion_wav_to_mp3()
    print("\nAll tests passed!")
