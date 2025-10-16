"""Job management data structures."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass
class Job:
    """Represents a single file conversion job."""
    id: str
    src_path: str
    src_mime: str
    dst_mime: str
    options: dict = field(default_factory=dict)
    status: str = Status.QUEUED.value
    progress: float = 0.0
    logs: list[str] = field(default_factory=list)
    output_path: Optional[str] = None
    
    def add_log(self, message: str) -> None:
        """Add a log message to the job."""
        self.logs.append(message)
    
    def set_status(self, status: Status) -> None:
        """Update job status."""
        self.status = status.value
    
    def set_progress(self, progress: float) -> None:
        """Update job progress (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
