# Plugin Specification

File Converter uses a plugin-based architecture for format conversions. This document describes how to create plugins.

## Plugin Structure

Each plugin is a directory under `src/file_converter/plugins/` containing:

- `plugin.toml` - Plugin metadata and configuration
- `plugin.py` - Python module implementing the plugin interface

## plugin.toml Format

```toml
name = "plugin_name"
version = "0.1.0"
entry = "plugin.py"
description = "Brief description"

tool_requires = ["tool>=version"]

[[capabilities]]
inputs = ["mime/type", "category/*"]
outputs = ["mime/type"]
```

### Fields

- `name` - Unique plugin identifier
- `version` - Semantic version
- `entry` - Python file name (usually "plugin.py")
- `description` - Human-readable description
- `tool_requires` - List of external tools required (e.g., "ffmpeg>=5")
- `capabilities` - List of conversion capabilities

## Plugin Interface

Every `plugin.py` must export four functions:

### `available() -> bool`

Check if plugin dependencies are available.

```python
import shutil

def available() -> bool:
    """Check if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None
```

### `capabilities() -> list[dict]`

Return plugin capabilities and parameter schemas.

```python
def capabilities() -> list[dict]:
    """Return plugin capabilities."""
    return [
        {
            "inputs": ["video/*", "audio/*"],
            "outputs": ["video/mp4", "audio/mp3"],
            "params": {
                "quality": {
                    "type": "int",
                    "min": 0,
                    "max": 51,
                    "default": 23,
                    "description": "Quality setting"
                },
                "preset": {
                    "type": "choice",
                    "choices": ["fast", "medium", "slow"],
                    "default": "medium",
                    "description": "Speed preset"
                }
            }
        }
    ]
```

### `plan(src_mime: str, dst_mime: str) -> dict`

Plan a conversion and return metadata.

```python
def plan(src_mime: str, dst_mime: str) -> dict:
    """Plan a conversion."""
    return {
        "cost": 1.0,  # Relative computational cost
        "lossiness": "lossy"  # or "lossless"
    }
```

### `run(src_path, dst_path, dst_mime, opts, progress_cb) -> None`

Execute the conversion.

```python
def run(src_path: str, dst_path: str, dst_mime: str,
        opts: dict, progress_cb: Callable[[str], None]) -> None:
    """Execute the conversion."""
    # Build command
    cmd = ["tool", "-i", src_path, "-o", dst_path]
    
    # Run with progress updates
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
    for line in process.stderr:
        progress_cb(line.rstrip())
    
    if process.wait() != 0:
        raise RuntimeError("Conversion failed")
```

## Example Plugin

Here's a minimal example:

**plugin.toml:**
```toml
name = "example_converter"
version = "0.1.0"
entry = "plugin.py"
description = "Example format converter"

tool_requires = ["example-tool>=1.0"]

[[capabilities]]
inputs = ["image/png"]
outputs = ["image/jpeg"]
```

**plugin.py:**
```python
import shutil
import subprocess
from typing import Callable

def available() -> bool:
    return shutil.which("convert") is not None

def capabilities() -> list[dict]:
    return [{
        "inputs": ["image/png"],
        "outputs": ["image/jpeg"],
        "params": {
            "quality": {
                "type": "int",
                "min": 0,
                "max": 100,
                "default": 90
            }
        }
    }]

def plan(src_mime: str, dst_mime: str) -> dict:
    return {"cost": 1.0, "lossiness": "lossy"}

def run(src_path: str, dst_path: str, dst_mime: str,
        opts: dict, progress_cb: Callable[[str], None]) -> None:
    quality = opts.get("quality", 90)
    cmd = ["convert", src_path, "-quality", str(quality), dst_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed: {result.stderr}")
    
    progress_cb(f"Converted to {dst_path}")
```

## Best Practices

1. **Error Handling**: Raise descriptive exceptions on failure
2. **Progress Updates**: Call `progress_cb` frequently with status updates
3. **Validation**: Validate options before running
4. **Resource Cleanup**: Clean up temporary files
5. **Testing**: Include availability checks that gracefully fail

## Parameter Types

Supported parameter types in capabilities:

- `int` - Integer with optional min/max
- `float` - Floating point with optional min/max
- `string` - Text string
- `choice` - One of predefined choices
- `bool` - True/False

Mark optional parameters with `"optional": true`.
