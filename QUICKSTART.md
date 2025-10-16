# Quick Start Guide

## Installation

### 1. System Dependencies
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install ffmpeg python3 python3-venv python3-pip

# Fedora
sudo dnf install ffmpeg python3

# macOS
brew install ffmpeg python3
```

### 2. Project Setup
```bash
cd /home/admin/Projects/file-converter

# Automated setup
./scripts/dev_setup.sh

# Manual setup (if needed)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### GUI Application

**Launch the GUI:**
```bash
./scripts/run_gui.sh
```

**Workflow:**
1. **Home** tab: Drag & drop files or click to browse
2. Select target format (MP4, WebM, GIF, MP3, FLAC)
3. Adjust options (quality, preset, scale, etc.)
4. Click "Add to Queue"
5. **Run Queue** tab: Click "Run Queue" to start conversion
6. Monitor real-time progress
7. Click "Open Output Folder" when done

### CLI

**Check if conversion is possible:**
```bash
./scripts/run_cli.sh plan input.mp4 --to audio/mp3
```

**Convert a file:**
```bash
# Basic conversion
./scripts/run_cli.sh run input.mp4 --to audio/mp3

# With options
./scripts/run_cli.sh run video.mkv --to video/mp4 \
  --opt crf=23 \
  --opt preset=medium \
  --out ./converted/

# Using presets
./scripts/run_cli.sh run video.mp4 --to video/mp4 --opt preset=web_1080p
```

## Common Conversions

### Video to Audio
```bash
# Extract audio as MP3
./scripts/run_cli.sh run video.mp4 --to audio/mp3

# Extract audio as FLAC (lossless)
./scripts/run_cli.sh run video.mp4 --to audio/flac
```

### Video Format Conversion
```bash
# Convert to web-friendly MP4
./scripts/run_cli.sh run input.mkv --to video/mp4 --opt preset=web_1080p

# Convert to WebM
./scripts/run_cli.sh run input.mp4 --to video/webm --opt crf=30
```

### Create GIF from Video
```bash
# Standard GIF
./scripts/run_cli.sh run video.mp4 --to image/gif

# Small GIF (custom)
./scripts/run_cli.sh run video.mp4 --to image/gif \
  --opt fps=12 \
  --opt scale=480:-1
```

### Audio Conversion
```bash
# WAV to MP3
./scripts/run_cli.sh run audio.wav --to audio/mp3 --opt quality=2

# MP3 to FLAC (lossless)
./scripts/run_cli.sh run audio.mp3 --to audio/flac
```

## Supported Formats

### Input
- **Video**: MP4, MKV, AVI, MOV, WebM, etc. (any FFmpeg-supported format)
- **Audio**: MP3, WAV, FLAC, OGG, AAC, etc. (any FFmpeg-supported format)

### Output
- **Video**: MP4, WebM
- **Image**: GIF (animated)
- **Audio**: MP3, FLAC

## Quality Settings

### MP4/WebM (CRF)
- **18**: Very high quality (large files)
- **23**: Balanced (default, recommended)
- **28**: Lower quality (smaller files)

### MP3 (Quality)
- **0**: ~245 kbps (high quality)
- **2**: ~190 kbps (standard, recommended)
- **5**: ~130 kbps (lower quality)

### GIF
- **fps**: 10-15 for web, 20+ for smooth animation
- **scale**: Use `480:-1` for small, `1080:-1` for HD

## Presets

Available presets in `config/defaults.toml`:

- **Video**: `web_1080p`, `web_720p`, `web_480p`, `high_quality`, `fast_encode`
- **GIF**: `gif_small`, `gif_medium`, `gif_large`
- **Audio**: `standard`, `high`, `low`

Use with: `--opt preset=web_1080p`

## Testing

```bash
# Run tests
source venv/bin/activate
python tests/test_detect.py
python tests/test_ffmpeg_video.py
```

## Troubleshooting

### FFmpeg not found
```bash
# Check if installed
which ffmpeg

# Install on Debian/Ubuntu
sudo apt install ffmpeg
```

### Python module errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### GUI doesn't start
```bash
# Check if Flet is installed
pip list | grep flet

# Run with PYTHONPATH
PYTHONPATH=src python -m file_converter.app
```

## Documentation

- **README.md**: Overview and installation
- **docs/plugin-spec.md**: Plugin development guide
- **docs/formats.md**: Detailed format reference
- **docs/presets.md**: Preset configuration guide
- **docs/PROGRESS.md**: Implementation status and roadmap

## Privacy

✅ **100% Local Processing**
- No data leaves your machine
- No telemetry or tracking
- No network access required
- All processing happens locally via FFmpeg

---

**Need help?** Check the [README.md](README.md) or [docs/](docs/) folder for detailed documentation.

