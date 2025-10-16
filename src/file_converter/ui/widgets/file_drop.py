"""File drop widget for drag-and-drop file selection."""
import flet as ft
from pathlib import Path
from typing import Callable, Optional


class FileDrop:
    """Drag-and-drop area for file selection."""
    
    def __init__(self, on_files_selected: Optional[Callable[[list[str]], None]] = None):
        self.on_files_selected = on_files_selected
        self.selected_files: list[str] = []
        self.file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        
        self.drop_container = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CLOUD_UPLOAD, size=48, color=ft.Colors.BLUE_400),
                    ft.Text("Drag files here or click to browse", size=16),
                    ft.Text("Supported: video, audio, images", 
                           size=12, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(2, ft.Colors.BLUE_400),
            border_radius=10,
            padding=40,
            bgcolor=ft.Colors.BLUE_50,
            height=200,
            alignment=ft.alignment.center,
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
        )
        
        self.control = ft.Column([
            self.file_picker,
            self.drop_container,
        ])
    
    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker results."""
        if e.files:
            self.selected_files = [f.path for f in e.files]
            
            # Update UI to show selected files count
            self.drop_container.content = ft.Column(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=48, color=ft.Colors.GREEN_400),
                    ft.Text(f"{len(self.selected_files)} file(s) selected", size=16),
                    ft.TextButton("Change selection", 
                                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True)),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.drop_container.border = ft.border.all(2, ft.Colors.GREEN_400)
            self.drop_container.bgcolor = ft.Colors.GREEN_50
            
            if self.on_files_selected:
                self.on_files_selected(self.selected_files)
            
            self.control.update()
    
    def clear(self):
        """Clear selected files."""
        self.selected_files = []
        self.drop_container.content = ft.Column(
            [
                ft.Icon(ft.Icons.CLOUD_UPLOAD, size=48, color=ft.Colors.BLUE_400),
                ft.Text("Drag files here or click to browse", size=16),
                ft.Text("Supported: video, audio, images", 
                       size=12, color=ft.Colors.GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        self.drop_container.border = ft.border.all(2, ft.Colors.BLUE_400)
        self.drop_container.bgcolor = ft.Colors.BLUE_50
        self.control.update()
