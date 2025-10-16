"""Subprocess execution wrapper with progress callbacks."""
import subprocess
from typing import Callable, Optional
from collections import deque


class ExecutionError(Exception):
    """Raised when a subprocess exits with non-zero status."""
    
    def __init__(self, message: str, returncode: int, stderr_tail: list[str]):
        super().__init__(message)
        self.returncode = returncode
        self.stderr_tail = stderr_tail


def run_command(
    cmd: list[str],
    progress_cb: Optional[Callable[[str], None]] = None,
    cwd: Optional[str] = None
) -> None:
    """
    Run a command with line-buffered stderr and progress callback.
    
    Args:
        cmd: Command and arguments as list
        progress_cb: Optional callback for each stderr line
        cwd: Working directory
        
    Raises:
        ExecutionError: On non-zero exit with last 50 lines of stderr
    """
    stderr_lines = deque(maxlen=50)
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            cwd=cwd
        )
        
        # Read stderr line by line
        if process.stderr:
            for line in process.stderr:
                line = line.rstrip()
                stderr_lines.append(line)
                if progress_cb:
                    progress_cb(line)
        
        # Wait for completion
        returncode = process.wait()
        
        if returncode != 0:
            raise ExecutionError(
                f"Command failed with exit code {returncode}: {' '.join(cmd)}",
                returncode,
                list(stderr_lines)
            )
            
    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            f"Failed to execute command: {e}",
            -1,
            list(stderr_lines)
        )
