"""Main entry point for the Flet GUI application."""
import flet as ft
from .ui.app_shell import main


if __name__ == "__main__":
    ft.app(target=main)
