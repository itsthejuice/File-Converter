# Supported Formats

This document lists the file formats currently supported by File Converter.

## Current Support (MVP)

### Video Formats

#### Inputs
- `video/*` - All video formats supported by FFmpeg
  - MP4, WebM, MKV, AVI, MOV, etc.

#### Outputs
- `video/mp4` - MPEG-4 video (H.264 + AAC)
- `video/webm` - WebM video (VP9 + Opus)
- `image/gif` - Animated GIF (with palette optimization)

### Audio Formats

#### Inputs
- `audio/*` - All audio formats supported by FFmpeg
  - MP3, WAV, FLAC, OGG, AAC, etc.

#### Outputs
- `audio/mp3` - MP3 audio (lossy)
- `audio/flac` - FLAC audio (lossless)

## Common Conversion Paths

### Video → Video
- MP4 → WebM (web optimization)
- MKV → MP4 (compatibility)
- Any video → GIF (animation/preview)

### Video → Audio
- MP4 → MP3 (extract audio)
- Any video → FLAC (lossless audio extract)

### Audio → Audio
- WAV → MP3 (compression)
- MP3 → FLAC (lossless archive)
- Any audio → MP3 (standardization)

## Quality Settings

### MP4 Video
- **CRF**: 0-51 (lower = better quality)
  - 18: High quality
  - 23: Default balanced
  - 28: Fast/smaller files
- **Preset**: ultrafast, veryfast, fast, medium, slow, slower, veryslow
  - Faster = larger files, quicker encoding
  - Slower = smaller files, better quality

### WebM Video
- **CRF**: 15-35 (lower = better quality)
  - 30: Default for web
- Similar presets as MP4

### GIF
- **FPS**: Frame rate (8-30 typical)
  - 12: Default smooth animation
  - 24: High frame rate
- **Scale**: Resolution (e.g., "480:-1", "1920:1080")

### MP3 Audio
- **Quality**: 0-9 (lower = better quality)
  - 0: ~245 kbps
  - 2: ~190 kbps (default)
  - 5: ~130 kbps

## Planned Support (Future)

### Image Formats (ImageMagick plugin)
- PNG, JPEG, WebP, TIFF, BMP
- PDF (single/multi-page)

### Document Formats (Pandoc plugin)
- Markdown ↔ HTML
- Markdown ↔ PDF
- DOCX ↔ Markdown
- EPUB ↔ PDF

### OCR (Tesseract plugin)
- Image/PDF → Text
- PDF → Searchable PDF

## Tool Requirements

### Current
- **FFmpeg** (v5.0+) - Video/audio conversion
  - Debian/Ubuntu: `apt install ffmpeg`
  - Fedora: `dnf install ffmpeg`
  - macOS: `brew install ffmpeg`

### Future
- **ImageMagick** - Image conversion
- **Pandoc** - Document conversion
- **Tesseract** - OCR

## MIME Type Reference

| Extension | MIME Type         | Category |
|-----------|-------------------|----------|
| .mp4      | video/mp4         | Video    |
| .webm     | video/webm        | Video    |
| .mkv      | video/x-matroska  | Video    |
| .gif      | image/gif         | Image    |
| .mp3      | audio/mpeg        | Audio    |
| .flac     | audio/flac        | Audio    |
| .wav      | audio/wav         | Audio    |
| .ogg      | audio/ogg         | Audio    |
| .jpg      | image/jpeg        | Image    |
| .png      | image/png         | Image    |
| .webp     | image/webp        | Image    |
| .pdf      | application/pdf   | Document |
