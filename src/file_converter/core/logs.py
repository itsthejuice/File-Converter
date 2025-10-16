"""Lightweight structured logging."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Logger:
    """Simple structured logger for the application."""
    
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = Path.home() / ".local" / "share" / "file-converter" / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "app.log"
    
    def log(self, level: str, message: str, **extra: Any) -> None:
        """
        Write a structured log entry.
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
            **extra: Additional fields
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **extra
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass  # Silent failure for logging
    
    def info(self, message: str, **extra: Any) -> None:
        """Log an info message."""
        self.log('INFO', message, **extra)
    
    def warning(self, message: str, **extra: Any) -> None:
        """Log a warning message."""
        self.log('WARNING', message, **extra)
    
    def error(self, message: str, **extra: Any) -> None:
        """Log an error message."""
        self.log('ERROR', message, **extra)


# Global logger instance
_logger = Logger()


def get_logger() -> Logger:
    """Get the global logger instance."""
    return _logger
