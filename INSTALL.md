# Installation & Quick Start Guide

## 🚀 Quick Start (3 Steps)

### 1. Run Setup Script

This will create a virtual environment, install all dependencies, and check for required tools:

```bash
cd /home/admin/Projects/file-converter
./scripts/dev_setup.sh
```

The script will:
- ✅ Create a Python virtual environment
- ✅ Install all Python dependencies (PySide6, python-magic, etc.)
- ✅ Check for required system tools (ffmpeg, etc.)
- ✅ Print installation hints for missing tools

### 2. Install FFmpeg (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg libmagic1
```

**Verify installation:**
```bash
ffmpeg -version
```

### 3. Launch the Application

**GUI Mode:**
```bash
./scripts/run_gui.sh
```

**CLI Mode:**
```bash
# List available plugins
./scripts/run_cli.sh list

# Convert a file
./scripts/run_cli.sh run input.mp4 --to audio/mp3
```

## 📋 What Gets Installed

### Python Dependencies
- **PySide6**: Qt GUI framework
- **python-magic**: MIME type detection
- **pluggy**: Plugin system support
- **tomli**: TOML configuration parsing
- **colorama**: Colored terminal output

### System Dependencies (Optional but Recommended)
- **ffmpeg**: Video/audio conversion (required for v0.1.0)
- **libmagic1**: MIME detection library
- **libxcb-xinerama0**: Qt display support

## 🧪 Testing the Installation

### Run Tests

```bash
source venv/bin/activate
python tests/test_detect.py
python tests/test_ffmpeg_video.py
```

### Try a Conversion

**Create a test audio file:**
```bash
# Generate a 1-second sine wave (requires ffmpeg)
ffmpeg -f lavfi -i "sine=frequency=440:duration=1" test_input.wav

# Convert to MP3
./scripts/run_cli.sh run test_input.wav --to audio/mp3

# Check output
ls -lh output/test_input.mp3
```

### Launch the GUI

```bash
./scripts/run_gui.sh
```

Then:
1. Drag a video or audio file into the window
2. Select target format (e.g., `audio/mp3`)
3. Click "Run Batch Conversion"
4. Watch the progress bar and logs

## 🔧 Troubleshooting

### "Permission denied" when running scripts

```bash
chmod +x scripts/*.sh
```

### "Module not found" errors

Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

Or run through the wrapper scripts:
```bash
./scripts/run_gui.sh  # Activates venv automatically
```

### FFmpeg not found

Install ffmpeg:
```bash
sudo apt install ffmpeg
```

Then verify:
```bash
which ffmpeg
ffmpeg -version
```

### GUI doesn't start (Qt issues)

Install Qt dependencies:
```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

### Import errors with python-magic

Install libmagic:
```bash
sudo apt install libmagic1
```

## 📦 Manual Installation (Advanced)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "from PySide6 import QtWidgets; print('PySide6 OK')"
python -c "import magic; print('python-magic OK')"

# Run GUI
python -m src.file_converter.app

# Or CLI
python -m cli.main list
```

## 🎯 Next Steps

Once installed:

1. **Read the README**: [README.md](README.md) for feature overview
2. **Check formats**: [docs/formats.md](docs/formats.md) for supported conversions
3. **Learn presets**: [docs/presets.md](docs/presets.md) for optimization tips
4. **Create plugins**: [docs/plugin-spec.md](docs/plugin-spec.md) to add formats

## 📊 System Requirements

**Minimum:**
- Python 3.10+
- 500 MB disk space
- 2 GB RAM

**Recommended:**
- Python 3.11+
- 2 GB disk space (for conversions)
- 4 GB RAM
- Multi-core CPU

**Tested On:**
- Ubuntu 22.04+
- Debian 11+
- Linux Mint 21+

**Should Work On:**
- macOS 11+ (with Homebrew)
- Windows 10+ (with WSL2)
- Any Linux distribution with Python 3.10+

---

**Need Help?** Check [README.md](README.md) or open an issue on GitHub.

