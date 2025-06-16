"""
Project Structure Healer
========================

Automatically fixes project structure issues.
"""

from pathlib import Path
from typing import List, Dict


class ProjectStructureHealer:
    """Heals project structure issues"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def heal(self) -> List[Dict]:
        """Attempt to heal project structure issues"""
        actions = []
        
        # Create missing directories
        required_dirs = [
            ".claude",
            ".claude/reports", 
            ".claude/patterns",
            ".claude/memory",
            "docs",
            "tests"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    actions.append({
                        'type': 'directory_created',
                        'path': dir_path,
                        'success': True,
                        'message': f'Created directory {dir_path}'
                    })
                except Exception as e:
                    actions.append({
                        'type': 'directory_creation_failed',
                        'path': dir_path,
                        'success': False,
                        'message': f'Failed to create {dir_path}: {e}'
                    })
        
        return actions