"""Progress chip widget showing job status and progress."""
import flet as ft
from ...core.jobs import Status


class ProgressChip:
    """Displays job progress as a chip with color and percentage."""
    
    def __init__(self, status: str = Status.QUEUED.value, progress: float = 0.0):
        self.status = status
        self.progress = progress
        
        color, text = self._get_status_display()
        
        if self.status == Status.RUNNING.value:
            percentage = f"{int(self.progress * 100)}%"
            display_text = f"{text} {percentage}"
        else:
            display_text = text
        
        self.text_control = ft.Text(display_text, size=12, color=ft.Colors.WHITE)
        
        self.control = ft.Container(
            content=self.text_control,
            bgcolor=color,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )
    
    def update_progress(self, status: str, progress: float):
        """Update the progress display."""
        self.status = status
        self.progress = progress
        
        color, text = self._get_status_display()
        
        if self.status == Status.RUNNING.value:
            percentage = f"{int(self.progress * 100)}%"
            display_text = f"{text} {percentage}"
        else:
            display_text = text
        
        self.text_control.value = display_text
        self.control.bgcolor = color
        self.control.update()
    
    def _get_status_display(self) -> tuple[str, str]:
        """Get color and text for current status."""
        status_map = {
            Status.QUEUED.value: (ft.Colors.GREY_500, "Queued"),
            Status.RUNNING.value: (ft.Colors.BLUE_500, "Running"),
            Status.DONE.value: (ft.Colors.GREEN_500, "Done"),
            Status.ERROR.value: (ft.Colors.RED_500, "Error"),
        }
        return status_map.get(self.status, (ft.Colors.GREY_500, "Unknown"))
