"""Job row widget for displaying job information."""
import flet as ft
from pathlib import Path
from ...core.jobs import Job
from .progress_chip import ProgressChip


class JobRow:
    """Displays a single job in the queue."""
    
    def __init__(self, job: Job, on_remove: callable = None):
        self.job = job
        self.on_remove = on_remove
        self.progress_chip = ProgressChip(job.status, job.progress)
        
        filename = Path(self.job.src_path).name
        
        # Format MIME types
        src_display = self._format_mime(self.job.src_mime)
        dst_display = self._format_mime(self.job.dst_mime)
        
        self.control = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=24),
                    ft.Column(
                        [
                            ft.Text(filename, weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"{src_display} → {dst_display}", 
                                   size=12, color=ft.Colors.GREY_600),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    self.progress_chip.control,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Remove",
                        on_click=self._on_remove_click,
                        visible=self.job.status in ["queued", "error"],
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
        )
    
    def set_progress(self, status: str, progress: float):
        """Update job progress."""
        self.job.status = status
        self.job.progress = progress
        self.progress_chip.update_progress(status, progress)
    
    def _format_mime(self, mime: str) -> str:
        """Format MIME type for display."""
        if not mime:
            return "unknown"
        
        # Simple mapping for common types
        mime_display = {
            'video/mp4': 'MP4',
            'video/webm': 'WebM',
            'image/gif': 'GIF',
            'audio/mp3': 'MP3',
            'audio/mpeg': 'MP3',
            'audio/flac': 'FLAC',
        }
        
        return mime_display.get(mime, mime.split('/')[-1].upper())
    
    def _on_remove_click(self, e):
        """Handle remove button click."""
        if self.on_remove:
            self.on_remove(self.job)
