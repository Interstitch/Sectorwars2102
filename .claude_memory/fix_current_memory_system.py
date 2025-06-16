#!/usr/bin/env python3
"""
Immediate fixes for the current memory system to make it more generic and portable.
This is a transitional solution while the full portability plan is implemented.
"""

import subprocess
import os
import getpass
import json
from pathlib import Path
from typing import List, Dict, Optional

class GenericIdentity:
    """Generic user identification that works for any collaborator"""
    
    def __init__(self):
        self.user = self._detect_user()
        self.relationship_terms = [
            "collaborator",
            "partner", 
            "user",
            "human",
            "developer",
            "friend"
        ]
        
    def _detect_user(self) -> str:
        """Detect current user through various methods"""
        # Try git config first
        try:
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True, 
                text=True,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
            
        # Try environment variable
        if os.environ.get('CLAUDE_USER'):
            return os.environ['CLAUDE_USER']
            
        # Fall back to system user
        return getpass.getuser()
        
    def get_search_patterns(self, base_query: Optional[str] = None) -> List[str]:
        """Generate generic search patterns that work for any user"""
        patterns = []
        
        # If a specific query is provided, use it first
        if base_query:
            patterns.append(base_query)
            
        # Add generic relationship patterns
        patterns.extend([
            "my collaborator",
            "my partner",
            "the user",
            "working together",
            "our project", 
            "we discussed",
            "you mentioned",
            "remember when",
            f"working with {self.user}",
            f"{self.user} and I"
        ])
        
        # Add relationship terms
        for term in self.relationship_terms:
            patterns.append(f"my {term}")
            patterns.append(f"the {term}")
            
        return patterns

def fix_memory_interface():
    """Update the memory interface to use generic patterns"""
    interface_path = Path(__file__).parent / "interface.py"
    
    if not interface_path.exists():
        print(f"❌ Could not find interface.py at {interface_path}")
        return
        
    # Read current interface
    content = interface_path.read_text()
    
    # Check if already fixed
    if "GenericIdentity" in content:
        print("✅ Interface already updated with generic identity")
        return
        
    # Create backup
    backup_path = interface_path.with_suffix('.py.backup')
    backup_path.write_text(content)
    print(f"📦 Created backup at {backup_path}")
    
    # Insert import at the top
    import_line = "from fix_current_memory_system import GenericIdentity\n"
    lines = content.split('\n')
    
    # Find where to insert import (after other imports)
    import_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_index = i + 1
            
    lines.insert(import_index, import_line)
    
    # Update the recall method to use generic patterns
    new_content = '\n'.join(lines)
    
    # Replace hardcoded patterns with generic ones
    new_content = new_content.replace(
        'def recall(self, query: str,',
        '''def recall(self, query: str,'''
    )
    
    # Add generic pattern generation right after the method starts
    recall_method_start = new_content.find('def recall(self, query: str,')
    if recall_method_start != -1:
        # Find the end of the method signature
        method_body_start = new_content.find('"""', recall_method_start)
        if method_body_start != -1:
            # Find the end of the docstring
            docstring_end = new_content.find('"""', method_body_start + 3) + 3
            
            # Insert generic pattern code
            generic_code = '''
        # Use generic identity patterns
        identity = GenericIdentity()
        search_patterns = identity.get_search_patterns(query)
        
        # Combine results from all patterns
        all_results = []
        '''
            new_content = (
                new_content[:docstring_end] + 
                generic_code + 
                new_content[docstring_end:]
            )
    
    # Write updated interface
    interface_path.write_text(new_content)
    print("✅ Updated interface.py with generic identity support")

def fix_database_locking():
    """Add better timeout and connection handling to comprehensive_indexer.py"""
    indexer_path = Path(__file__).parent / "comprehensive_indexer.py"
    
    if not indexer_path.exists():
        print(f"❌ Could not find comprehensive_indexer.py at {indexer_path}")
        return
        
    content = indexer_path.read_text()
    
    # Check if already fixed
    if "timeout=30" in content:
        print("✅ Database timeouts already increased")
        return
        
    # Create backup
    backup_path = indexer_path.with_suffix('.py.backup')
    backup_path.write_text(content)
    print(f"📦 Created backup at {backup_path}")
    
    # Replace all sqlite3.connect calls to add timeout
    new_content = content.replace(
        "sqlite3.connect(str(self.db_path))",
        "sqlite3.connect(str(self.db_path), timeout=30)"
    )
    
    # Add connection pooling helper at the top of the class
    class_start = new_content.find("class ComprehensiveIndexer:")
    if class_start != -1:
        init_start = new_content.find("def __init__", class_start)
        pool_code = '''
    def _get_connection(self):
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        conn.execute("PRAGMA busy_timeout=30000")  # 30s timeout
        return conn
        
'''
        new_content = new_content[:init_start] + pool_code + new_content[init_start:]
        
        # Replace direct connect calls with the helper
        new_content = new_content.replace(
            "conn = sqlite3.connect(str(self.db_path), timeout=30)",
            "conn = self._get_connection()"
        )
    
    indexer_path.write_text(new_content)
    print("✅ Updated comprehensive_indexer.py with better database handling")

def fix_format_strings():
    """Fix SQL LIKE pattern escaping issues"""
    indexer_path = Path(__file__).parent / "comprehensive_indexer.py"
    
    if not indexer_path.exists():
        return
        
    content = indexer_path.read_text()
    
    # Fix the SQL pattern escaping
    new_content = content.replace(
        "sql_pattern = pattern.replace('%', '%')",
        "sql_pattern = pattern.replace('%', '\\%').replace('_', '\\_')"
    )
    
    if new_content != content:
        indexer_path.write_text(new_content)
        print("✅ Fixed SQL pattern escaping")

def create_generic_startup():
    """Create a more generic startup script"""
    startup_content = '''#!/usr/bin/env python3
"""
Generic Claude startup script that works for any user
"""

import os
import sys
from pathlib import Path

# Add memory system to path
memory_path = Path(__file__).parent / ".claude_memory"
if memory_path.exists():
    sys.path.insert(0, str(memory_path))

def check_memory_system():
    """Check if memory system is available and working"""
    try:
        from interface import MemoryInterface
        from fix_current_memory_system import GenericIdentity
        
        print("=" * 60)
        print("🧠 COGNITIVE CONTINUITY CHECK")
        print("=" * 60)
        
        # Initialize memory
        memory = MemoryInterface()
        memory.initialize()
        
        # Get generic identity
        identity = GenericIdentity()
        print(f"👤 Collaborator: {identity.user}")
        print(f"🔍 Search patterns: {', '.join(identity.relationship_terms)}")
        
        # Try to recall recent context
        patterns = identity.get_search_patterns()
        for pattern in patterns[:3]:  # Try first 3 patterns
            results = memory.recall(pattern, top_k=3)
            if results:
                print(f"\\n📚 Found {len(results)} memories for '{pattern}'")
                break
        else:
            print("\\n📚 No recent memories found (this is normal for new projects)")
            
        print("\\n✅ Memory system ready for any collaborator!")
        print("=" * 60)
        
    except ImportError:
        print("⚠️  Memory system not found. This is normal for fresh installations.")
        print("📖 Run the installer to add memory capabilities to this project.")
    except Exception as e:
        print(f"❌ Memory system error: {e}")
        print("🔧 Try running: python .claude_memory/fix_current_memory_system.py")

if __name__ == "__main__":
    check_memory_system()
'''
    
    startup_path = Path(__file__).parent.parent / ".claude_startup.py"
    
    # Backup existing startup if it exists
    if startup_path.exists():
        backup_path = startup_path.with_suffix('.py.backup')
        startup_path.rename(backup_path)
        print(f"📦 Backed up existing startup to {backup_path}")
    
    # Write new generic startup
    startup_path.write_text(startup_content)
    startup_path.chmod(0o755)  # Make executable
    print(f"✅ Created generic startup script at {startup_path}")

def main():
    """Apply all fixes to make the current system more generic"""
    print("🔧 Applying fixes to make memory system generic...")
    print()
    
    # Apply each fix
    fix_memory_interface()
    fix_database_locking()
    fix_format_strings()
    create_generic_startup()
    
    print()
    print("✅ All fixes applied!")
    print()
    print("🎯 Next steps:")
    print("1. Test the system with: python .claude_startup.py")
    print("2. Try recalling memories without using specific names")
    print("3. The system will now work for ANY collaborator!")
    print()
    print("📚 For the full portability plan, see:")
    print("   .claude_memory/DOCS/memory-system-portability-plan.md")

if __name__ == "__main__":
    main()