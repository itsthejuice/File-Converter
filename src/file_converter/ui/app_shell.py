"""Main application shell with navigation."""
import flet as ft
from pathlib import Path
from ..core.registry import Registry
from ..core.presets import load_defaults
from ..core.jobs import Job
from .pages.home import HomePage
from .pages.run_queue import RunQueuePage
from .pages.settings import SettingsPage


class AppState:
    """Shared application state."""
    
    def __init__(self):
        self.registry = Registry()
        self.presets = {}
        self.jobs: list[Job] = []
        self.output_dir: str = ""
        self.config = {}
        
        # Load plugins
        plugin_dir = Path(__file__).parent.parent / "plugins"
        self.registry.load_plugins(plugin_dir)
        
        # Load presets
        self.presets = load_defaults()


def main(page: ft.Page):
    """Main application entry point."""
    page.title = "File Converter (Local)"
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    page.padding = 0
    
    # Initialize app state
    state = AppState()
    
    # Create pages
    home_page = HomePage(page, state)
    queue_page = RunQueuePage(page, state)
    settings_page = SettingsPage(page, state)
    
    # Navigation state
    current_page = [0]  # Use list to allow mutation in closure
    
    def route_change(e):
        """Handle navigation changes."""
        if e.control.selected_index == 0:
            content_area.content = home_page.build()
        elif e.control.selected_index == 1:
            content_area.content = queue_page.build()
        elif e.control.selected_index == 2:
            content_area.content = settings_page.build()
        
        current_page[0] = e.control.selected_index
        page.update()
    
    # Navigation rail
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.QUEUE_OUTLINED,
                selected_icon=ft.Icons.QUEUE,
                label="Run Queue",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=route_change,
    )
    
    # Content area
    content_area = ft.Container(
        content=home_page.build(),
        expand=True,
        padding=20,
    )
    
    # Main layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )

