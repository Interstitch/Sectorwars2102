"""
Missing Files Healer
====================

Automatically creates missing essential files.
"""

from pathlib import Path
from typing import List, Dict


class MissingFilesHealer:
    """Heals missing essential files"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def heal(self) -> List[Dict]:
        """Attempt to heal missing files"""
        actions = []
        
        # Create .gitignore if missing
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """# CLAUDE.md system
.claude/cache/
.claude/reports/*.json
!.claude/reports/.gitkeep

# Common development files
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
dist/
build/
"""
            try:
                gitignore_path.write_text(gitignore_content)
                actions.append({
                    'type': 'file_created',
                    'path': '.gitignore',
                    'success': True,
                    'message': 'Created .gitignore file'
                })
            except Exception as e:
                actions.append({
                    'type': 'file_creation_failed',
                    'path': '.gitignore',
                    'success': False,
                    'message': f'Failed to create .gitignore: {e}'
                })
        
        return actions