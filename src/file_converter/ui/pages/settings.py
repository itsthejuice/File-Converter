"""Settings page for application configuration."""
import flet as ft
from pathlib import Path
import shutil


class SettingsPage:
    """Page for application settings."""
    
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state
    
    def build(self):
        """Build the settings page UI."""
        # Output directory picker
        self.output_dir_picker = ft.FilePicker(on_result=self._on_output_dir_selected)
        
        self.output_dir_field = ft.TextField(
            label="Output Directory",
            hint_text="Leave empty to use source file directory",
            value=self.state.output_dir,
            read_only=True,
            expand=True,
        )
        
        output_dir_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Browse",
            on_click=lambda _: self.output_dir_picker.get_directory_path(),
        )
        
        # FFmpeg path
        ffmpeg_path = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
        self.ffmpeg_field = ft.TextField(
            label="FFmpeg Path",
            value=ffmpeg_path,
            read_only=True,
            expand=True,
        )
        
        # Check if ffmpeg is available
        ffmpeg_available = shutil.which("ffmpeg") is not None
        ffmpeg_status = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE if ffmpeg_available else ft.Icons.ERROR,
                    color=ft.Colors.GREEN if ffmpeg_available else ft.Colors.RED,
                    size=20,
                ),
                ft.Text(
                    "FFmpeg is available" if ffmpeg_available else "FFmpeg not found",
                    color=ft.Colors.GREEN if ffmpeg_available else ft.Colors.RED,
                ),
            ]),
            padding=10,
        )
        
        # Privacy notice
        privacy_notice = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PRIVACY_TIP, color=ft.Colors.BLUE_600),
                    ft.Text("Privacy & Security", size=18, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text(
                    "• All conversions run locally on your machine\n"
                    "• No data is sent to external servers\n"
                    "• No telemetry or tracking\n"
                    "• No network access required",
                    size=14,
                ),
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_300),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
        )
        
        # System info
        available_plugins = self.state.registry.get_available_plugins()
        plugin_list = ft.Column([
            ft.Text(f"• {p.name} v{p.version}") 
            for p in available_plugins
        ] or [ft.Text("No plugins available", color=ft.Colors.GREY_600)])
        
        system_info = ft.Container(
            content=ft.Column([
                ft.Text("Loaded Plugins", size=18, weight=ft.FontWeight.BOLD),
                plugin_list,
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )
        
        return ft.Column(
            [
                self.output_dir_picker,
                
                ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Text("Paths", size=20, weight=ft.FontWeight.BOLD),
                
                ft.Row([
                    self.output_dir_field,
                    output_dir_button,
                ]),
                
                self.ffmpeg_field,
                ffmpeg_status,
                
                ft.Divider(),
                
                privacy_notice,
                
                ft.Divider(),
                
                system_info,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _on_output_dir_selected(self, e: ft.FilePickerResultEvent):
        """Handle output directory selection."""
        if e.path:
            self.state.output_dir = e.path
            self.output_dir_field.value = e.path
            self.page.update()

