# File Converter

A local-only file conversion tool with a modern Flet GUI and plugin-based architecture.

## Features

✨ **Privacy First**
- 🔒 100% local processing - no data leaves your machine
- 🚫 No telemetry or tracking
- 🔌 No network access required
- 📝 Open source and auditable

🎯 **User Friendly**
- 🖱️ Modern drag-and-drop GUI
- ⌨️ Powerful CLI for automation
- 📊 Real-time progress tracking
- 🎨 Preset-based workflow

🔧 **Extensible**
- 🧩 Plugin-based architecture
- 📦 Easy to add new formats
- ⚙️ Configurable presets
- 🔨 Leverages existing tools (FFmpeg, etc.)

## Current Support

### Video Conversions
- Video → MP4 (H.264 + AAC)
- Video → WebM (VP9 + Opus)
- Video → GIF (animated)

### Audio Conversions
- Audio → MP3 (lossy)
- Audio → FLAC (lossless)
- Video → Audio (extract)

**Supported input formats**: Any video or audio format supported by FFmpeg (MP4, MKV, AVI, MOV, MP3, WAV, FLAC, OGG, etc.)

## System Requirements

### Required Tools

- **FFmpeg** (v5.0+) - for video/audio conversion

### Debian/Ubuntu Quick Start

```bash
# Install system dependencies
sudo apt update
sudo apt install ffmpeg python3 python3-venv python3-pip

# Clone and setup
git clone <repository-url>
cd file-converter

# Run development setup
./scripts/dev_setup.sh

# Launch GUI
./scripts/run_gui.sh

# Or use CLI
./scripts/run_cli.sh plan input.mp4 --to audio/mp3
./scripts/run_cli.sh run input.mp4 --to audio/mp3 --out ./converted/
```

## Installation

### From Source

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python -m file_converter.app

# Or install as package
pip install -e .

# Then use the CLI command
fc run input.mp4 --to video/webm --opt crf=30
```

### System Tools

**Debian/Ubuntu:**
```bash
sudo apt install ffmpeg
```

**Fedora/RHEL:**
```bash
sudo dnf install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

## Usage

### GUI

1. **Select Files**: Drag and drop or click to browse
2. **Choose Format**: Select target format from dropdown
3. **Configure Options**: Adjust quality, presets, etc.
4. **Add to Queue**: Queue up multiple conversions
5. **Run**: Process all jobs with real-time progress

### CLI

**Plan a conversion** (check if possible):
```bash
fc plan input.mp4 --to video/webm
```

**Run a conversion**:
```bash
# Basic conversion
fc run input.mp4 --to audio/mp3

# With options
fc run video.mkv --to video/mp4 --opt crf=23 --opt preset=medium

# Custom output directory
fc run video.mov --to video/webm --out ./converted/

# Using presets
fc run video.mp4 --to video/mp4 --opt preset=web_1080p
```

## Configuration

### Presets

Edit `config/defaults.toml` to customize presets:

```toml
[presets.video_mp4]
web_1080p = { crf = 23, preset = "medium", scale = "1920:1080" }
my_custom = { crf = 20, preset = "slow" }

[presets.image_gif]
tiny = { fps = 10, scale = "320:-1" }
```

See [docs/presets.md](docs/presets.md) for details.

### Tool Paths

Customize tool locations in `config/toolpaths.toml` (copy from `toolpaths.example.toml`).

## Development

### Project Structure

```
file-converter/
├── src/file_converter/      # Main package
│   ├── core/               # Conversion engine
│   ├── plugins/            # Format plugins
│   └── ui/                 # Flet GUI
├── cli/                    # CLI interface
├── tests/                  # Unit tests
├── config/                 # Configuration files
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

### Running Tests

```bash
source venv/bin/activate
python tests/test_detect.py
python tests/test_ffmpeg_video.py
```

### Creating Plugins

See [docs/plugin-spec.md](docs/plugin-spec.md) for the plugin API.

Example plugin structure:
```
src/file_converter/plugins/my_plugin/
├── plugin.toml    # Metadata
└── plugin.py      # Implementation
```

## Documentation

- [Plugin Specification](docs/plugin-spec.md) - How to create plugins
- [Supported Formats](docs/formats.md) - Complete format reference
- [Presets Guide](docs/presets.md) - Preset configuration
- [Progress Log](docs/PROGRESS.md) - Implementation status

## Privacy & Security

🔒 **This application is designed for complete privacy:**

- All conversions run locally on your machine
- No data is uploaded to any server
- No telemetry, analytics, or tracking
- No network connections required
- No external API calls

The only external dependency is the system tools you install (FFmpeg, etc.), which run locally.

## Roadmap

### Implemented ✅
- [x] Flet GUI with drag-and-drop
- [x] Plugin-based architecture
- [x] FFmpeg video/audio plugin
- [x] Real-time progress tracking
- [x] CLI interface
- [x] Preset system
- [x] MIME type detection
- [x] Batch processing

### Planned 🚧
- [ ] Multi-hop conversions (e.g., WMA → WAV → FLAC)
- [ ] ImageMagick plugin (PNG, JPEG, WebP, PDF)
- [ ] Pandoc plugin (Markdown, HTML, DOCX, PDF)
- [ ] Tesseract plugin (OCR)
- [ ] Concurrent workers
- [ ] Watch folders (auto-convert)
- [ ] GPU acceleration options
- [ ] Enhanced preset editor in GUI

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Areas of interest:

- New plugins (ImageMagick, Pandoc, etc.)
- UI/UX improvements
- Performance optimizations
- Documentation
- Bug reports

## Support

- 📚 Check the [docs/](docs/) directory
- 🐛 Report issues on GitHub
- 💡 Request features via issues

---

**Made with ❤️ for privacy-conscious users**
