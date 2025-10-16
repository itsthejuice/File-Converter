"""Home page for file selection and job configuration."""
import flet as ft
from pathlib import Path
import uuid
from ...core.detect import sniff_mime
from ...core.jobs import Job
from ...core.planner import get_supported_outputs
from ..widgets.file_drop import FileDrop


class HomePage:
    """Home page with file drop and conversion options."""
    
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state
        self.selected_files = []
        self.detected_mimes = {}
        self.selected_format = None
        self.options = {}
    
    def build(self):
        """Build the home page UI."""
        # File drop widget
        self.file_drop = FileDrop(on_files_selected=self._on_files_selected)
        
        # File list
        self.file_list = ft.Column([], spacing=5)
        
        # Target format dropdown
        self.format_dropdown = ft.Dropdown(
            label="Target Format",
            hint_text="Select output format",
            options=[
                ft.dropdown.Option("video/mp4", "MP4 Video"),
                ft.dropdown.Option("video/webm", "WebM Video"),
                ft.dropdown.Option("image/gif", "GIF Animation"),
                ft.dropdown.Option("audio/mp3", "MP3 Audio"),
                ft.dropdown.Option("audio/flac", "FLAC Audio (Lossless)"),
            ],
            on_change=self._on_format_change,
            width=300,
        )
        
        # Options panel
        self.options_panel = ft.Column([], spacing=10)
        
        # Add to queue button
        self.add_button = ft.ElevatedButton(
            "Add to Queue",
            icon=ft.Icons.ADD_TO_QUEUE,
            on_click=self._on_add_to_queue,
            disabled=True,
        )
        
        return ft.Column(
            [
                ft.Text("File Converter", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Local-only conversion with no telemetry or network access",
                       size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
                
                ft.Text("1. Select Files", size=20, weight=ft.FontWeight.BOLD),
                self.file_drop.control,
                self.file_list,
                
                ft.Divider(),
                
                ft.Text("2. Choose Format", size=20, weight=ft.FontWeight.BOLD),
                self.format_dropdown,
                
                ft.Divider(),
                
                ft.Text("3. Options", size=20, weight=ft.FontWeight.BOLD),
                self.options_panel,
                
                ft.Divider(),
                
                self.add_button,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _on_files_selected(self, files: list[str]):
        """Handle file selection."""
        self.selected_files = files
        self.detected_mimes = {}
        
        # Detect MIME types
        self.file_list.controls.clear()
        for file_path in files:
            try:
                mime = sniff_mime(file_path)
                self.detected_mimes[file_path] = mime
                
                filename = Path(file_path).name
                mime_display = mime.split('/')[-1].upper()
                
                self.file_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=20),
                            ft.Text(filename, expand=True),
                            ft.Text(mime_display, size=12, color=ft.Colors.BLUE_600),
                        ]),
                        padding=5,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                    )
                )
            except Exception as e:
                self.file_list.controls.append(
                    ft.Text(f"Error: {Path(file_path).name} - {e}", 
                           color=ft.Colors.RED_600)
                )
        
        self._update_add_button()
        self.page.update()
    
    def _on_format_change(self, e):
        """Handle format selection change."""
        self.selected_format = e.control.value
        self._update_options_panel()
        self._update_add_button()
    
    def _update_options_panel(self):
        """Update the options panel based on selected format and plugin."""
        self.options_panel.controls.clear()
        self.options = {}
        
        if not self.selected_format:
            self.page.update()
            return
        
        # Get plugin capabilities
        # For now, show common options based on format
        if self.selected_format in ["video/mp4", "video/webm"]:
            # CRF
            crf_slider = ft.Slider(
                min=0, max=51, value=23, divisions=51, label="{value}",
                on_change=lambda e: self._set_option("crf", int(e.control.value))
            )
            self.options["crf"] = 23
            
            self.options_panel.controls.append(
                ft.Column([
                    ft.Text("Quality (CRF): Lower = Better", size=14),
                    crf_slider,
                ])
            )
            
            # Preset
            preset_dropdown = ft.Dropdown(
                label="Speed Preset",
                value="veryfast",
                options=[
                    ft.dropdown.Option("ultrafast"),
                    ft.dropdown.Option("veryfast"),
                    ft.dropdown.Option("fast"),
                    ft.dropdown.Option("medium"),
                    ft.dropdown.Option("slow"),
                ],
                on_change=lambda e: self._set_option("preset", e.control.value),
                width=200,
            )
            self.options["preset"] = "veryfast"
            self.options_panel.controls.append(preset_dropdown)
            
        elif self.selected_format == "image/gif":
            # FPS
            fps_field = ft.TextField(
                label="Frame Rate (FPS)",
                value="12",
                width=150,
                on_change=lambda e: self._set_option("fps", int(e.control.value) if e.control.value.isdigit() else 12)
            )
            self.options["fps"] = 12
            self.options_panel.controls.append(fps_field)
            
            # Scale
            scale_field = ft.TextField(
                label="Scale (e.g., 480:-1)",
                hint_text="Optional",
                width=200,
                on_change=lambda e: self._set_option("scale", e.control.value)
            )
            self.options_panel.controls.append(scale_field)
        
        elif self.selected_format == "audio/mp3":
            # Quality
            quality_slider = ft.Slider(
                min=0, max=9, value=2, divisions=9, label="{value}",
                on_change=lambda e: self._set_option("quality", int(e.control.value))
            )
            self.options["quality"] = 2
            
            self.options_panel.controls.append(
                ft.Column([
                    ft.Text("Quality: Lower = Better", size=14),
                    quality_slider,
                ])
            )
        
        self.page.update()
    
    def _set_option(self, key: str, value):
        """Set an option value."""
        if value:
            self.options[key] = value
        elif key in self.options:
            del self.options[key]
    
    def _update_add_button(self):
        """Update the state of the Add to Queue button."""
        self.add_button.disabled = not (self.selected_files and self.selected_format)
        self.page.update()
    
    def _on_add_to_queue(self, e):
        """Add selected files to the job queue."""
        for file_path in self.selected_files:
            src_mime = self.detected_mimes.get(file_path, "application/octet-stream")
            
            job = Job(
                id=str(uuid.uuid4()),
                src_path=file_path,
                src_mime=src_mime,
                dst_mime=self.selected_format,
                options=self.options.copy(),
            )
            
            self.state.jobs.append(job)
        
        # Clear selection
        self.file_drop.clear()
        self.selected_files = []
        self.detected_mimes = {}
        self.file_list.controls.clear()
        self.selected_format = None
        self.format_dropdown.value = None
        self.options = {}
        self.options_panel.controls.clear()
        self._update_add_button()
        
        # Show confirmation
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Added {len(self.selected_files)} job(s) to queue"),
            bgcolor=ft.Colors.GREEN_600,
        )
        self.page.snack_bar.open = True
        self.page.update()

