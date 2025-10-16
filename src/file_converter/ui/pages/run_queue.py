"""Run queue page for managing and executing conversion jobs."""
import flet as ft
import threading
from pathlib import Path
from ...core.engine import run_batch
from ...core.jobs import Status
from ..widgets.job_row import JobRow


class RunQueuePage:
    """Page for viewing and running the job queue."""
    
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state
        self.is_running = False
    
    def build(self):
        """Build the run queue page UI."""
        # Job list
        self.job_list = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Buttons
        self.run_button = ft.ElevatedButton(
            "Run Queue",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_run_click,
            disabled=False,
        )
        
        self.clear_button = ft.OutlinedButton(
            "Clear Completed",
            icon=ft.Icons.CLEAR_ALL,
            on_click=self._on_clear_click,
        )
        
        self.open_folder_button = ft.OutlinedButton(
            "Open Output Folder",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._on_open_folder_click,
        )
        
        # Build initial job list
        self._refresh_job_list()
        
        return ft.Column(
            [
                ft.Row([
                    ft.Text("Run Queue", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text(f"({len(self.state.jobs)} jobs)", 
                           size=20, color=ft.Colors.GREY_600),
                ]),
                
                ft.Divider(),
                
                ft.Row([
                    self.run_button,
                    self.clear_button,
                    self.open_folder_button,
                ], spacing=10),
                
                ft.Divider(),
                
                self.job_list,
            ],
            expand=True,
        )
    
    def _refresh_job_list(self):
        """Refresh the job list display."""
        self.job_list.controls.clear()
        
        if not self.state.jobs:
            self.job_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=64, color=ft.Colors.GREY_400),
                        ft.Text("No jobs in queue", size=16, color=ft.Colors.GREY_600),
                        ft.Text("Add files from the Home page", 
                               size=12, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
        else:
            for job in self.state.jobs:
                job_row = JobRow(job, on_remove=self._on_remove_job)
                self.job_list.controls.append(job_row.control)
        
        self.page.update()
    
    def _on_run_click(self, e):
        """Start running the job queue."""
        if self.is_running:
            return
        
        queued_jobs = [j for j in self.state.jobs if j.status == Status.QUEUED.value]
        if not queued_jobs:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("No queued jobs to run"),
                bgcolor=ft.Colors.ORANGE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        self.is_running = True
        self.run_button.disabled = True
        self.run_button.text = "Running..."
        self.page.update()
        
        # Run in background thread
        def run_jobs():
            try:
                def on_update(job):
                    # Update UI on main thread using async wrapper
                    async def update_ui():
                        self._update_job_ui(job)
                    self.page.run_task(update_ui)
                
                run_batch(
                    self.state.jobs,
                    self.state.registry,
                    self.state.presets,
                    self.state.output_dir if self.state.output_dir else None,
                    on_update
                )
            finally:
                self.is_running = False
                async def complete_ui():
                    self._on_run_complete()
                self.page.run_task(complete_ui)
        
        threading.Thread(target=run_jobs, daemon=True).start()
    
    def _update_job_ui(self, job):
        """Update the UI for a specific job."""
        # Refresh the entire job list for now (simpler approach)
        self._refresh_job_list()
    
    def _on_run_complete(self):
        """Handle completion of batch run."""
        self.run_button.disabled = False
        self.run_button.text = "Run Queue"
        
        completed = sum(1 for j in self.state.jobs if j.status == Status.DONE.value)
        errors = sum(1 for j in self.state.jobs if j.status == Status.ERROR.value)
        
        message = f"Completed: {completed}"
        if errors:
            message += f", Errors: {errors}"
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREEN_600 if errors == 0 else ft.Colors.ORANGE_600,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_clear_click(self, e):
        """Clear completed and error jobs from the queue."""
        original_count = len(self.state.jobs)
        self.state.jobs = [
            j for j in self.state.jobs 
            if j.status not in [Status.DONE.value, Status.ERROR.value]
        ]
        removed = original_count - len(self.state.jobs)
        
        self._refresh_job_list()
        
        if removed > 0:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Removed {removed} job(s)"),
                bgcolor=ft.Colors.BLUE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_open_folder_click(self, e):
        """Open the output folder."""
        if self.state.output_dir:
            folder_path = self.state.output_dir
        else:
            # Use the first completed job's output directory
            completed_jobs = [j for j in self.state.jobs if j.output_path]
            if completed_jobs:
                folder_path = str(Path(completed_jobs[0].output_path).parent)
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No output folder available yet"),
                    bgcolor=ft.Colors.ORANGE_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
        
        # Try to open folder
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", folder_path])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", folder_path])
        except Exception:
            # Fallback: show path
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Output folder: {folder_path}"),
                bgcolor=ft.Colors.BLUE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_remove_job(self, job):
        """Remove a job from the queue."""
        if job in self.state.jobs:
            self.state.jobs.remove(job)
            self._refresh_job_list()

