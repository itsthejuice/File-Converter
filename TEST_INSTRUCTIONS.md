# Testing Instructions

## Quick Test

To verify the File Converter is working:

### 1. Install Dependencies

```bash
./scripts/dev_setup.sh
```

This will:
- Create virtual environment
- Install Flet and other dependencies
- Check for ffmpeg

### 2. Install FFmpeg (if not present)

```bash
sudo apt update
sudo apt install ffmpeg libmagic1
```

### 3. Test GUI

```bash
./scripts/run_gui.sh
```

Expected behavior:
- Flet window opens with "File Converter" title
- You see sections for:
  - Files to Convert (with "Add Files" button)
  - Target Format dropdown
  - Options panel
  - Conversion Jobs area
  - Logs section

### 4. Test Basic Conversion

**Option A: Using GUI**
1. Click "Add Files..." button
2. Select a video or audio file
3. Choose target format (e.g., "audio/mp3")
4. Click "Run Batch Conversion"
5. Watch progress in job list and logs
6. Check `output/` directory for result

**Option B: Using CLI**
```bash
# List plugins
./scripts/run_cli.sh list

# Create test audio (1 second sine wave)
ffmpeg -f lavfi -i "sine=frequency=440:duration=1" test.wav

# Convert to MP3
./scripts/run_cli.sh run test.wav --to audio/mp3

# Check output
ls -lh output/test.mp3
```

## What to Verify

### GUI Should Show:
- ✅ Clean Flet interface (not Qt/PySide)
- ✅ File picker button works
- ✅ Files appear in list with MIME types
- ✅ Format dropdown has 8 options
- ✅ Options panel updates when format changes
- ✅ Jobs appear with progress bars
- ✅ Status updates (Queued → Running → Done)
- ✅ Logs display conversion output
- ✅ Output files created in `output/` directory

### CLI Should Work:
- ✅ `fc list` shows ffmpeg_video plugin
- ✅ `fc plan input.wav --to audio/mp3` shows conversion plan
- ✅ `fc run input.wav --to audio/mp3` creates output file
- ✅ Progress shown in terminal
- ✅ Error messages are clear

## Common Issues

### "No module named 'flet'"
```bash
source venv/bin/activate
pip install flet
```

### "ffmpeg not found"
```bash
sudo apt install ffmpeg
```

### Import errors
Make sure you're in the project root:
```bash
cd /home/admin/Projects/file-converter
./scripts/run_gui.sh
```

## Success Criteria

✅ GUI opens without errors
✅ Can add files via file picker
✅ Can run conversion
✅ Progress updates in real-time
✅ Output file created and playable
✅ CLI works for all commands
✅ No Python exceptions in logs

