#!/usr/bin/env python3
"""Integration test for conversion workflow."""
import sys
import tempfile
import subprocess
from pathlib import Path

sys.path.insert(0, 'src')

from file_converter.core.registry import Registry
from file_converter.core.jobs import Job, Status
from file_converter.core.engine import plan_and_run
from file_converter.core.presets import load_defaults

print("=== File Converter Integration Test ===\n")

# Check if ffmpeg is available
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    if result.returncode != 0:
        print("❌ FFmpeg not available")
        sys.exit(1)
    print("✓ FFmpeg is available")
except Exception as e:
    print(f"❌ FFmpeg check failed: {e}")
    sys.exit(1)

# Create test audio file
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    input_file = tmpdir / "test_input.wav"
    
    print("\n1. Creating test audio file...")
    try:
        subprocess.run(
            [
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "1", "-y", str(input_file)
            ],
            capture_output=True,
            timeout=10,
            check=True
        )
        print(f"   ✓ Created test file: {input_file.name}")
    except Exception as e:
        print(f"   ❌ Failed to create test file: {e}")
        sys.exit(1)
    
    # Load plugin registry
    print("\n2. Loading plugin registry...")
    registry = Registry()
    plugin_dir = Path("src/file_converter/plugins")
    registry.load_plugins(plugin_dir)
    
    available = registry.get_available_plugins()
    print(f"   ✓ Loaded {len(available)} plugin(s)")
    for plugin in available:
        print(f"     - {plugin.name} v{plugin.version}")
    
    # Load presets
    print("\n3. Loading presets...")
    presets = load_defaults()
    print(f"   ✓ Loaded presets for {len(presets)} format(s)")
    
    # Create job
    print("\n4. Creating conversion job...")
    job = Job(
        id="test-integration-1",
        src_path=str(input_file),
        src_mime="audio/wav",
        dst_mime="audio/mp3",
        options={"quality": 2}
    )
    print(f"   ✓ Job created: {job.src_mime} → {job.dst_mime}")
    
    # Progress tracking
    progress_updates = []
    def on_progress(j):
        progress_updates.append(j.progress)
        if j.progress > 0:
            print(f"   Progress: {int(j.progress * 100)}%")
    
    # Run conversion
    print("\n5. Running conversion...")
    result = plan_and_run(job, registry, presets, str(tmpdir), on_progress)
    
    # Check results
    print("\n6. Checking results...")
    if result.status == Status.DONE.value:
        print(f"   ✓ Conversion completed successfully")
        print(f"   ✓ Output: {result.output_path}")
        
        output_file = Path(result.output_path)
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"   ✓ Output file exists: {size} bytes")
        else:
            print(f"   ❌ Output file not found")
            sys.exit(1)
        
        if len(progress_updates) > 0:
            print(f"   ✓ Progress updates received: {len(progress_updates)}")
        
    elif result.status == Status.ERROR.value:
        print(f"   ❌ Conversion failed")
        print(f"\n   Last logs:")
        for log in result.logs[-5:]:
            print(f"     {log}")
        sys.exit(1)
    else:
        print(f"   ⚠ Unexpected status: {result.status}")
        sys.exit(1)

print("\n=== Integration Test PASSED ===\n")

