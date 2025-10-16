"""Main application window using Flet."""

import flet as ft
from pathlib import Path
from typing import Dict, List
import threading

from ..core.engine import ConversionEngine
from ..core.jobs import Job, JobStatus
from ..core.detect import sniff_mime
from ..core.registry import get_global_registry


def create_job_row(job: Job) -> ft.Container:
    """Create a job row widget."""
    filename_text = ft.Text(Path(job.src_path).name, weight=ft.FontWeight.BOLD)
    format_text = ft.Text(
        f"{job.src_mime} → {job.dst_mime}",
        size=12,
        color=ft.Colors.GREY_700
    )
    progress_bar = ft.ProgressBar(value=0, width=300)
    status_text = ft.Text("Queued", size=14)
    
    return ft.Container(
        content=ft.Row([
            ft.Column([
                filename_text,
                format_text,
            ], spacing=2),
            progress_bar,
            status_text,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=5,
        margin=ft.margin.only(bottom=5),
        data={
            "job": job,
            "progress_bar": progress_bar,
            "status_text": status_text,
            "filename_text": filename_text
        }
    )


class MainWindow:
    """Main application window with file conversion."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "File Converter"
        self.page.window_width = 900
        self.page.window_height = 700
        self.page.padding = 20
        
        # Initialize engine and data
        self.engine = ConversionEngine()
        self.registry = get_global_registry()
        self.jobs: Dict[str, Job] = {}
        self.job_rows: Dict[str, ft.Container] = {}
        self.worker_thread = None
        
        # Connect callbacks
        self.engine.job_updated.connect(self._on_job_updated)
        self.engine.batch_complete.connect(self._on_batch_complete)
        
        # UI components
        self.file_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=150)
        self.job_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
        self.log_output = ft.Column(scroll=ft.ScrollMode.AUTO, height=150)
        
        self.format_dropdown = ft.Dropdown(
            label="Target Format",
            options=[
                ft.dropdown.Option("video/mp4"),
                ft.dropdown.Option("video/webm"),
                ft.dropdown.Option("image/gif"),
                ft.dropdown.Option("audio/mp3"),
                ft.dropdown.Option("audio/flac"),
                ft.dropdown.Option("image/png"),
                ft.dropdown.Option("image/jpeg"),
                ft.dropdown.Option("application/pdf"),
            ],
            value="video/mp4",
            on_change=self._on_format_changed,
            width=300
        )
        
        self.options_panel = ft.Column(spacing=10)
        self.run_button = ft.ElevatedButton(
            "Run Batch Conversion",
            on_click=self._run_batch,
            disabled=True,
            icon=ft.Icons.PLAY_ARROW
        )
        
        self._build_ui()
        self._update_options_panel()
    
    def _build_ui(self):
        """Build the user interface."""
        
        # File picker
        self.file_picker = ft.FilePicker(on_result=self._on_files_selected)
        self.page.overlay.append(self.file_picker)
        
        # Left side: File list
        left_panel = ft.Container(
            content=ft.Column([
                ft.Text("Files to Convert", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(
                    content=self.file_list,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=5,
                    padding=10,
                ),
                ft.ElevatedButton(
                    "Add Files...",
                    on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
                    icon=ft.Icons.ADD
                ),
            ], spacing=10),
            expand=2
        )
        
        # Right side: Options panel
        right_panel = ft.Container(
            content=ft.Column([
                ft.Text("Target Format", weight=ft.FontWeight.BOLD, size=16),
                self.format_dropdown,
                ft.Divider(),
                ft.Text("Options", weight=ft.FontWeight.BOLD, size=16),
                self.options_panel,
            ], spacing=10),
            expand=1
        )
        
        # Top section
        top_section = ft.Row([left_panel, right_panel], spacing=20)
        
        # Job list
        job_section = ft.Column([
            ft.Text("Conversion Jobs", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=self.job_list,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
            ),
            self.run_button,
        ], spacing=10)
        
        # Log pane
        log_section = ft.Column([
            ft.Text("Logs", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=self.log_output,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
                bgcolor=ft.Colors.GREY_900,
            ),
        ], spacing=10)
        
        # Main layout
        self.page.add(
            ft.Column([
                top_section,
                ft.Divider(),
                job_section,
                ft.Divider(),
                log_section,
            ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        )
    
    def _on_files_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection."""
        if not e.files:
            return
        
        file_paths = [f.path for f in e.files]
        self._add_files(file_paths)
    
    def _add_files(self, file_paths: List[str]):
        """Add files to the conversion queue."""
        for file_path in file_paths:
            try:
                # Detect MIME type
                mime = sniff_mime(file_path)
                filename = Path(file_path).name
                
                # Add to file list
                self.file_list.controls.append(
                    ft.Text(f"• {filename} ({mime})", size=12)
                )
                
                self._log(f"Added: {filename} ({mime})")
                
                # Create a job
                dst_mime = self.format_dropdown.value
                options = self._collect_options()
                
                job = self.engine.create_job(file_path, dst_mime, options)
                self.jobs[job.id] = job
                
                # Add to job list
                job_row = create_job_row(job)
                self.job_rows[job.id] = job_row
                self.job_list.controls.append(job_row)
                
            except Exception as ex:
                self._log(f"Error adding {file_path}: {ex}")
        
        # Enable run button if we have jobs
        self.run_button.disabled = len(self.jobs) == 0
        self.page.update()
    
    def _on_format_changed(self, e):
        """Handle format dropdown change."""
        self._update_options_panel()
    
    def _update_options_panel(self):
        """Update options panel based on selected format."""
        self.options_panel.controls.clear()
        
        dst_mime = self.format_dropdown.value
        
        # Find matching plugins
        converters = self.registry.match_converters("video/*", dst_mime)
        if not converters:
            converters = self.registry.match_converters("audio/*", dst_mime)
        
        if not converters:
            self.options_panel.controls.append(
                ft.Text("No options available", color=ft.Colors.GREY_600)
            )
            self.page.update()
            return
        
        # Get capabilities from first converter
        plugin = converters[0]
        caps = plugin.capabilities()
        
        if not caps:
            self.page.update()
            return
        
        params = caps[0].get("params", {})
        
        # Add option widgets
        for param_name, param_info in params.items():
            if param_info.get("default") is None:
                continue
            
            param_type = param_info.get("type")
            
            if param_type == "int":
                widget = ft.TextField(
                    label=param_name,
                    value=str(param_info.get("default", 0)),
                    width=200,
                    data=param_name,
                    hint_text=param_info.get("description", "")
                )
                self.options_panel.controls.append(widget)
                
            elif param_type == "str" and "choices" in param_info:
                widget = ft.Dropdown(
                    label=param_name,
                    options=[ft.dropdown.Option(c) for c in param_info["choices"]],
                    value=param_info.get("default"),
                    width=200,
                    data=param_name
                )
                self.options_panel.controls.append(widget)
                
            elif param_type == "str":
                widget = ft.TextField(
                    label=param_name,
                    value=param_info.get("default", ""),
                    width=200,
                    data=param_name,
                    hint_text=param_info.get("description", "")
                )
                self.options_panel.controls.append(widget)
        
        self.page.update()
    
    def _collect_options(self) -> dict:
        """Collect options from the options panel."""
        options = {}
        
        for control in self.options_panel.controls:
            if isinstance(control, ft.TextField) and control.data:
                value = control.value.strip()
                if value:
                    # Try to convert to int
                    try:
                        options[control.data] = int(value)
                    except ValueError:
                        options[control.data] = value
            elif isinstance(control, ft.Dropdown) and control.data:
                if control.value:
                    options[control.data] = control.value
        
        return options
    
    def _run_batch(self, e):
        """Run batch conversion in background thread."""
        if not self.jobs:
            return
        
        self._log("Starting batch conversion...")
        self.run_button.disabled = True
        self.page.update()
        
        # Update all jobs with current options
        dst_mime = self.format_dropdown.value
        options = self._collect_options()
        
        for job in self.jobs.values():
            job.dst_mime = dst_mime
            job.options = options
        
        # Run in background thread
        def run_conversions():
            job_list = list(self.jobs.values())
            self.engine.run_batch(job_list)
        
        self.worker_thread = threading.Thread(target=run_conversions, daemon=True)
        self.worker_thread.start()
    
    def _on_job_updated(self, job_id: str):
        """Handle job update signal."""
        job = self.jobs.get(job_id)
        if not job:
            return
        
        # Update widget
        row = self.job_rows.get(job_id)
        if row and row.data:
            data = row.data
            progress_bar = data["progress_bar"]
            status_text = data["status_text"]
            
            progress_bar.value = job.progress
            
            # Update status
            status_map = {
                JobStatus.QUEUED: ("Queued", ft.Colors.GREY_700),
                JobStatus.RUNNING: ("Running...", ft.Colors.BLUE),
                JobStatus.DONE: ("Done ✓", ft.Colors.GREEN),
                JobStatus.ERROR: ("Error ✗", ft.Colors.RED)
            }
            
            status_str, color = status_map.get(job.status, ("Unknown", ft.Colors.GREY))
            status_text.value = status_str
            status_text.color = color
            
            self.page.update()
        
        # Log status changes
        if job.logs:
            last_log = job.logs[-1]
            if "ERROR" in last_log or job.status == JobStatus.ERROR:
                self._log(f"[{Path(job.src_path).name}] {last_log}")
    
    def _on_batch_complete(self):
        """Handle batch completion."""
        self._log("Batch conversion complete!")
        
        # Show summary
        done = sum(1 for j in self.jobs.values() if j.status == JobStatus.DONE)
        errors = sum(1 for j in self.jobs.values() if j.status == JobStatus.ERROR)
        
        self._log(f"Results: {done} succeeded, {errors} failed")
        
        # Show outputs
        for job in self.jobs.values():
            if job.output_path:
                self._log(f"Output: {job.output_path}")
        
        self.run_button.disabled = False
        self.page.update()
    
    def _log(self, message: str):
        """Add message to log pane."""
        self.log_output.controls.append(
            ft.Text(message, size=12, color=ft.Colors.GREEN_300)
        )
        
        # Keep only last 100 log lines
        if len(self.log_output.controls) > 100:
            self.log_output.controls.pop(0)
        
        self.page.update()


def create_app(page: ft.Page):
    """Create the main application."""
    MainWindow(page)
