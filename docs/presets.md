# Presets Guide

Presets are predefined sets of conversion options for common use cases. They make it easy to get good results without tweaking individual parameters.

## Using Presets

### GUI
1. Select your target format
2. In the Options panel, choose a preset from the dropdown (if available)
3. You can still override individual settings after selecting a preset

### CLI
```bash
fc run input.mp4 --to video/mp4 --opt preset=web_1080p
```

## Built-in Presets

### Video (MP4)

#### `web_1080p`
Balanced quality for web streaming at 1080p.
- CRF: 23
- Preset: medium
- Scale: 1920×1080

#### `web_720p`
Balanced quality for web streaming at 720p.
- CRF: 23
- Preset: medium
- Scale: 1280×720

#### `web_480p`
Smaller files for mobile or slower connections.
- CRF: 23
- Preset: fast
- Scale: 854×480

#### `high_quality`
High quality archival encoding.
- CRF: 18 (near lossless)
- Preset: slow
- Original resolution

#### `fast_encode`
Quick encoding for previews or testing.
- CRF: 28
- Preset: ultrafast
- Original resolution

### Video (WebM)

#### `web_1080p`
Standard WebM for web use at 1080p.
- CRF: 30
- Preset: medium
- Scale: 1920×1080

#### `web_720p`
Standard WebM for web use at 720p.
- CRF: 30
- Preset: medium
- Scale: 1280×720

### GIF

#### `gif_small`
Small animated GIF for sharing.
- FPS: 12
- Scale: 480px width (maintains aspect ratio)

#### `gif_medium`
Medium quality animated GIF.
- FPS: 15
- Scale: 720px width

#### `gif_large`
High quality animated GIF.
- FPS: 20
- Scale: 1080px width

### Audio (MP3)

#### `standard`
Good quality for most purposes (~190 kbps).
- Quality: 2

#### `high`
High quality for music (~245 kbps).
- Quality: 0

#### `low`
Smaller files for voice/podcasts (~130 kbps).
- Quality: 5

### Audio (FLAC)

#### `default`
Lossless audio compression.
- No additional options (always lossless)

## Custom Presets

You can define custom presets in `config/defaults.toml`:

```toml
[presets.video_mp4]
my_custom = { crf = 20, preset = "medium", scale = "1440:1080" }

[presets.image_gif]
tiny = { fps = 10, scale = "320:-1" }
```

## FFmpeg Option Reference

### CRF (Constant Rate Factor)
Controls quality vs. file size tradeoff.

**H.264 (MP4):**
- 0-17: Visually lossless
- 18: High quality
- 23: Default (good balance)
- 28: Noticeable compression
- 51: Worst quality

**VP9 (WebM):**
- 15-25: High quality
- 30: Default for web
- 35-50: Lower quality

### Preset
Encoding speed/efficiency tradeoff. Does NOT affect quality, only encode time and file size.

- `ultrafast`: Fastest encoding, largest files
- `veryfast`: Very fast, good for real-time
- `fast`: Fast encoding
- `medium`: Default balanced
- `slow`: Better compression
- `slower`: Even better compression
- `veryslow`: Best compression, slowest

### Scale
Resize video to specific resolution.

Format: `width:height` or `width:-1` (maintain aspect ratio)

Examples:
- `1920:1080` - Full HD
- `1280:720` - HD
- `854:480` - 480p
- `640:-1` - 640px wide, auto height
- `-1:720` - Auto width, 720px tall

### FPS (Frames Per Second)
For GIF output, controls smoothness vs. file size.

- 8-10: Choppy but small
- 12-15: Good balance (default: 12)
- 20-24: Smooth animation
- 30+: Very smooth, larger files

### Audio Quality (MP3)
VBR quality setting (0-9, lower = better).

- 0: ~245 kbps (high quality)
- 2: ~190 kbps (standard, default)
- 4: ~165 kbps
- 5: ~130 kbps (low quality)
- 9: ~65 kbps (very low)

## Tips

1. **Start with presets**: They're tuned for common scenarios
2. **Web video**: Use `web_720p` for best compatibility
3. **Archival**: Use `high_quality` for MP4 or FLAC for audio
4. **GIF optimization**: Lower FPS and resolution significantly reduce file size
5. **Override selectively**: Presets can be combined with manual options
6. **Test first**: Try on a short clip before batch converting

## Future Enhancements

- Preset editor in GUI
- Preset import/export
- Automatic preset suggestion based on input
- Quality estimation preview
