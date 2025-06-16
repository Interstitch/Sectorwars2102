"""
File Management Utilities
==========================

Safe file operations and utilities.
"""

from pathlib import Path
from typing import List, Optional


class FileManager:
    """Manages file operations safely"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def read_safe(self, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if not possible"""
        try:
            return file_path.read_text(encoding='utf-8')
        except:
            try:
                return file_path.read_text(encoding='latin-1')
            except:
                return None
    
    def write_safe(self, file_path: Path, content: str) -> bool:
        """Safely write a file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return True
        except:
            return False
    
    def find_files(self, pattern: str, exclude_dirs: List[str] = None) -> List[Path]:
        """Find files matching pattern, excluding specified directories"""
        if exclude_dirs is None:
            exclude_dirs = ['node_modules', '.git', 'vendor', 'build', 'dist', '__pycache__']
        
        files = list(self.project_root.rglob(pattern))
        filtered = []
        
        for file_path in files:
            if not any(excluded in str(file_path) for excluded in exclude_dirs):
                filtered.append(file_path)
        
        return filtered