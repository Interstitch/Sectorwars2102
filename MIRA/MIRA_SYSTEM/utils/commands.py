"""
Command Execution Utilities
============================

Safe command execution utilities.
"""

import subprocess
from pathlib import Path
from typing import Tuple, Optional


class CommandRunner:
    """Executes shell commands safely"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def run(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = True) -> Tuple[bool, str]:
        """Run shell command safely"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    cwd=cwd or self.project_root, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                return result.returncode == 0, result.stdout + result.stderr
            else:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    cwd=cwd or self.project_root, 
                    timeout=30
                )
                return result.returncode == 0, ""
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return False, str(e)