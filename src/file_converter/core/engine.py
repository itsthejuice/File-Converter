"""Conversion engine - orchestrates the conversion process."""
import json
import re
from pathlib import Path
from typing import Optional, Callable
from .jobs import Job, Status
from .registry import Registry
from .planner import plan_conversion
from .detect import sniff_mime


def plan_and_run(
    job: Job,
    registry: Registry,
    presets: dict,
    out_dir: Optional[str] = None,
    on_progress: Optional[Callable[[Job], None]] = None
) -> Job:
    """
    Plan and execute a single conversion job.
    
    Args:
        job: Job to execute
        registry: Plugin registry
        presets: Preset configurations
        out_dir: Output directory (if None, use source directory)
        on_progress: Optional callback for progress updates
        
    Returns:
        Updated job with results
    """
    try:
        job.set_status(Status.RUNNING)
        job.add_log(f"Starting conversion: {job.src_mime} -> {job.dst_mime}")
        
        if on_progress:
            on_progress(job)
        
        # Detect source MIME if not set
        if not job.src_mime:
            job.src_mime = sniff_mime(job.src_path)
            job.add_log(f"Detected MIME type: {job.src_mime}")
        
        # Plan conversion
        plan = plan_conversion(job.src_mime, job.dst_mime, registry)
        if not plan:
            raise ValueError(f"No conversion route found for {job.src_mime} -> {job.dst_mime}")
        
        job.add_log(f"Using plugin: {plan['plugin'].name}")
        
        # Apply presets if specified
        options = job.options.copy()
        preset_name = options.pop('preset', None)
        if preset_name and job.dst_mime in presets:
            preset_opts = presets[job.dst_mime].get(preset_name, {})
            # Preset values can be overridden by explicit options
            merged = preset_opts.copy()
            merged.update(options)
            options = merged
        
        # Determine output path
        src_path = Path(job.src_path)
        if out_dir:
            out_dir_path = Path(out_dir)
            out_dir_path.mkdir(parents=True, exist_ok=True)
            base_name = src_path.stem
        else:
            out_dir_path = src_path.parent
            base_name = src_path.stem
        
        # Get extension from MIME type
        extension = _mime_to_extension(job.dst_mime)
        output_path = out_dir_path / f"{base_name}{extension}"
        
        # Handle name conflicts
        counter = 1
        while output_path.exists():
            output_path = out_dir_path / f"{base_name}_{counter}{extension}"
            counter += 1
        
        job.output_path = str(output_path)
        job.add_log(f"Output: {job.output_path}")
        
        # Progress callback with MIME context for duration extraction
        duration = _extract_duration(job.src_path)
        
        def progress_callback(line: str):
            job.add_log(line)
            # Try to parse ffmpeg progress
            progress = _parse_ffmpeg_progress(line, duration)
            if progress is not None:
                job.set_progress(progress)
                if on_progress:
                    on_progress(job)
        
        # Run conversion
        plan['plugin'].run(
            job.src_path,
            str(output_path),
            job.dst_mime,
            options,
            progress_callback
        )
        
        # Verify output
        if not output_path.exists():
            raise RuntimeError("Output file was not created")
        
        job.set_status(Status.DONE)
        job.set_progress(1.0)
        job.add_log("Conversion completed successfully")
        
        # Write job report
        _write_job_report(job, output_path)
        
    except Exception as e:
        job.set_status(Status.ERROR)
        job.add_log(f"Error: {str(e)}")
        
    if on_progress:
        on_progress(job)
    
    return job


def run_batch(
    jobs: list[Job],
    registry: Registry,
    presets: dict,
    out_dir: Optional[str] = None,
    on_update: Optional[Callable[[Job], None]] = None
) -> None:
    """
    Run multiple jobs sequentially (MVP - no parallelization).
    
    Args:
        jobs: List of jobs to execute
        registry: Plugin registry
        presets: Preset configurations
        out_dir: Output directory
        on_update: Callback for job updates
    """
    for job in jobs:
        if job.status == Status.QUEUED.value:
            plan_and_run(job, registry, presets, out_dir, on_update)


def _mime_to_extension(mime: str) -> str:
    """Convert MIME type to file extension."""
    mime_map = {
        'video/mp4': '.mp4',
        'video/webm': '.webm',
        'video/x-matroska': '.mkv',
        'image/gif': '.gif',
        'audio/mp3': '.mp3',  # Non-standard but used in our plugin
        'audio/mpeg': '.mp3',
        'audio/flac': '.flac',
        'audio/wav': '.wav',
        'audio/ogg': '.ogg',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp',
        'application/pdf': '.pdf',
        'text/plain': '.txt',
    }
    return mime_map.get(mime, '.bin')


def _extract_duration(file_path: str) -> Optional[float]:
    """Try to extract duration from media file using ffprobe."""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass
    return None


def _parse_ffmpeg_progress(line: str, duration: Optional[float]) -> Optional[float]:
    """
    Parse ffmpeg progress from stderr line.
    
    Looks for time= in ffmpeg output and estimates percentage.
    """
    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
    if match:
        hours, minutes, seconds = match.groups()
        current = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        
        if duration and duration > 0:
            return min(0.95, current / duration)  # Cap at 95% until done
        else:
            # Pulse mode - just indicate activity
            return 0.5
    
    return None


def _write_job_report(job: Job, output_path: Path) -> None:
    """Write a JSON report alongside the output file."""
    report = {
        'job_id': job.id,
        'src_path': job.src_path,
        'src_mime': job.src_mime,
        'dst_mime': job.dst_mime,
        'output_path': job.output_path,
        'status': job.status,
        'options': job.options,
    }
    
    report_path = output_path.parent / f"{output_path.stem}_job_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
    except Exception:
        pass  # Non-critical
