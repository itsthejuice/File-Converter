"""FFmpeg video/audio conversion plugin."""
import shutil
import subprocess
import re
from typing import Callable
from pathlib import Path


def available() -> bool:
    """Check if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None


def capabilities() -> list[dict]:
    """Return plugin capabilities."""
    return [
        {
            "inputs": ["video/*", "audio/*"],
            "outputs": ["video/mp4", "video/webm", "image/gif", "audio/mp3", "audio/flac"],
            "params": {
                "crf": {
                    "type": "int",
                    "min": 0,
                    "max": 51,
                    "default": 23,
                    "description": "Constant Rate Factor (lower = higher quality)"
                },
                "preset": {
                    "type": "choice",
                    "choices": ["ultrafast", "superfast", "veryfast", "faster", "fast", 
                               "medium", "slow", "slower", "veryslow"],
                    "default": "veryfast",
                    "description": "Encoding speed preset"
                },
                "scale": {
                    "type": "string",
                    "optional": True,
                    "description": "Scale filter (e.g., 1920:1080, 720:-1)"
                },
                "fps": {
                    "type": "int",
                    "optional": True,
                    "description": "Frame rate (for GIF)"
                },
                "quality": {
                    "type": "int",
                    "optional": True,
                    "description": "Audio quality (for MP3: 0-9, lower is better)"
                }
            }
        }
    ]


def plan(src_mime: str, dst_mime: str) -> dict:
    """
    Plan a conversion.
    
    Returns metadata about the planned conversion.
    """
    lossiness = "lossy"
    
    # Lossless formats
    if dst_mime == "audio/flac":
        lossiness = "lossless"
    
    return {
        "cost": 1.0,
        "lossiness": lossiness
    }


def run(src_path: str, dst_path: str, dst_mime: str, 
        opts: dict, progress_cb: Callable[[str], None]) -> None:
    """
    Execute the conversion using ffmpeg.
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
        dst_mime: Target MIME type
        opts: Conversion options
        progress_cb: Progress callback for stderr lines
    """
    # Build ffmpeg command based on output format
    if dst_mime == "video/mp4":
        cmd = _build_mp4_command(src_path, dst_path, opts)
    elif dst_mime == "video/webm":
        cmd = _build_webm_command(src_path, dst_path, opts)
    elif dst_mime == "image/gif":
        cmd = _build_gif_command(src_path, dst_path, opts)
    elif dst_mime == "audio/mp3":
        cmd = _build_mp3_command(src_path, dst_path, opts)
    elif dst_mime == "audio/flac":
        cmd = _build_flac_command(src_path, dst_path, opts)
    else:
        raise ValueError(f"Unsupported output format: {dst_mime}")
    
    # Execute command
    _run_ffmpeg(cmd, progress_cb)


def _build_mp4_command(src: str, dst: str, opts: dict) -> list[str]:
    """Build command for MP4 output."""
    cmd = ["ffmpeg", "-i", src, "-y"]
    
    # Video codec
    cmd.extend(["-c:v", "libx264"])
    cmd.extend(["-pix_fmt", "yuv420p"])
    
    # CRF
    crf = opts.get("crf", 23)
    cmd.extend(["-crf", str(crf)])
    
    # Preset
    preset = opts.get("preset", "veryfast")
    cmd.extend(["-preset", preset])
    
    # Scale
    if "scale" in opts:
        cmd.extend(["-vf", f"scale={opts['scale']}"])
    
    # Audio codec
    cmd.extend(["-c:a", "aac"])
    cmd.extend(["-b:a", "128k"])
    
    cmd.append(dst)
    return cmd


def _build_webm_command(src: str, dst: str, opts: dict) -> list[str]:
    """Build command for WebM output."""
    cmd = ["ffmpeg", "-i", src, "-y"]
    
    # Video codec (VP9)
    cmd.extend(["-c:v", "libvpx-vp9"])
    
    # CRF for VP9
    crf = opts.get("crf", 30)
    cmd.extend(["-crf", str(crf)])
    cmd.extend(["-b:v", "0"])  # Constant quality mode
    
    # Scale
    if "scale" in opts:
        cmd.extend(["-vf", f"scale={opts['scale']}"])
    
    # Audio codec
    cmd.extend(["-c:a", "libopus"])
    cmd.extend(["-b:a", "128k"])
    
    cmd.append(dst)
    return cmd


def _build_gif_command(src: str, dst: str, opts: dict) -> list[str]:
    """
    Build command for GIF output using palettegen/paletteuse.
    
    This uses a two-pass approach for better quality.
    """
    fps = opts.get("fps", 12)
    scale = opts.get("scale", "480:-1")
    
    # Generate palette
    palette_path = Path(dst).parent / "palette.png"
    
    # First pass: generate palette
    cmd_palette = [
        "ffmpeg", "-i", src, "-y",
        "-vf", f"fps={fps},scale={scale}:flags=lanczos,palettegen",
        str(palette_path)
    ]
    
    _run_ffmpeg(cmd_palette, lambda x: None)  # Silent for palette gen
    
    # Second pass: use palette
    cmd = [
        "ffmpeg", "-i", src, "-i", str(palette_path), "-y",
        "-lavfi", f"fps={fps},scale={scale}:flags=lanczos[x];[x][1:v]paletteuse",
        dst
    ]
    
    return cmd


def _build_mp3_command(src: str, dst: str, opts: dict) -> list[str]:
    """Build command for MP3 output."""
    cmd = ["ffmpeg", "-i", src, "-y"]
    
    # Audio codec
    cmd.extend(["-c:a", "libmp3lame"])
    
    # Quality
    quality = opts.get("quality", 2)
    cmd.extend(["-q:a", str(quality)])
    
    cmd.append(dst)
    return cmd


def _build_flac_command(src: str, dst: str, opts: dict) -> list[str]:
    """Build command for FLAC output (lossless)."""
    cmd = ["ffmpeg", "-i", src, "-y"]
    
    # Audio codec (lossless)
    cmd.extend(["-c:a", "flac"])
    
    cmd.append(dst)
    return cmd


def _run_ffmpeg(cmd: list[str], progress_cb: Callable[[str], None]) -> None:
    """Run ffmpeg command and stream stderr to callback."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Read stderr line by line
        stderr_lines = []
        if process.stderr:
            for line in process.stderr:
                line = line.rstrip()
                stderr_lines.append(line)
                progress_cb(line)
        
        returncode = process.wait()
        
        if returncode != 0:
            error_msg = "\n".join(stderr_lines[-20:])  # Last 20 lines
            raise RuntimeError(f"FFmpeg failed with code {returncode}:\n{error_msg}")
            
    except Exception as e:
        raise RuntimeError(f"FFmpeg execution failed: {e}")
