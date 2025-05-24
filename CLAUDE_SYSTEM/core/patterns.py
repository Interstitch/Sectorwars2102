"""
Pattern Analysis Module
=======================

Analyzes patterns in code and git history for learning.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys
sys.path.append(str(Path(__file__).parent))
from data_structures import Pattern
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner


class PatternAnalyzer:
    """Analyzes patterns for learning and prediction"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.patterns = {}
        self.commands = CommandRunner(project_root)
        self.patterns_dir = project_root / ".claude" / "patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_git_history(self) -> None:
        """Analyze git commit patterns"""
        print("    📖 Analyzing git history patterns...")
        
        try:
            success, output = self.commands.run('git log --oneline -100')
            if not success:
                print("        ⚠️  No git history available")
                return
                
            commits = output.strip().split('\n')
            
            # Analyze commit patterns
            fix_commits = [c for c in commits if re.search(r'fix|bug|issue', c, re.I)]
            feature_commits = [c for c in commits if re.search(r'feat|add|implement', c, re.I)]
            refactor_commits = [c for c in commits if re.search(r'refactor|clean|improve', c, re.I)]
            
            print(f"        ✓ Analyzed {len(commits)} commits")
            print(f"          - Fixes: {len(fix_commits)}")
            print(f"          - Features: {len(feature_commits)}")
            print(f"          - Refactors: {len(refactor_commits)}")
            
            # Record patterns if significant
            if len(fix_commits) > 5:
                self._record_pattern(Pattern(
                    id="frequent-fixes",
                    type="bug",
                    description="High frequency of bug fixes detected",
                    occurrences=len(fix_commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Increase test coverage and code review", "success_rate": 0.8}],
                    predictors=["low-test-coverage", "rapid-development"]
                ))
            
            if len(feature_commits) > 0:
                self._record_pattern(Pattern(
                    id="feature-development",
                    type="feature",
                    description=f"Active feature development detected ({len(feature_commits)} feature commits)",
                    occurrences=len(feature_commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Maintain feature development velocity", "success_rate": 0.9}],
                    predictors=["active-development"]
                ))
            
            if len(commits) > 30:  # Active development
                self._record_pattern(Pattern(
                    id="active-development",
                    type="development",
                    description=f"High development activity ({len(commits)} recent commits)",
                    occurrences=len(commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Maintain development momentum while ensuring quality", "success_rate": 0.8}],
                    predictors=["rapid-development", "feature-focus"]
                ))
            
        except Exception as e:
            print(f"        ⚠️  Could not analyze git history: {e}")
    
    def analyze_code_patterns(self) -> None:
        """Analyze code structure patterns"""
        print("    🔍 Analyzing code patterns...")
        
        # Check test patterns
        test_files = list(self.project_root.rglob("*test*.py"))
        test_files.extend(list(self.project_root.rglob("*.test.js")))
        test_files.extend(list(self.project_root.rglob("*.spec.ts")))
        
        src_files = list(self.project_root.rglob("**/*.py"))
        src_files.extend(list(self.project_root.rglob("**/*.js")))
        src_files.extend(list(self.project_root.rglob("**/*.ts")))
        src_files = [f for f in src_files if 'test' not in str(f).lower()]
        
        test_ratio = len(test_files) / len(src_files) if src_files else 0
        
        if test_ratio < 0.3:  # Low test coverage pattern
            self._record_pattern(Pattern(
                id="low-test-coverage",
                type="testing",
                description=f"Low test coverage pattern detected (ratio: {test_ratio:.2f})",
                occurrences=1,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                context=["code-analysis"],
                solutions=[{"description": "Implement comprehensive test strategy", "success_rate": 0.9}],
                predictors=["quality-issues", "bug-risk"]
            ))
        
        # Check TODO patterns
        success, output = self.commands.run('grep -r "TODO\\|FIXME\\|BUG\\|HACK" . --include="*.py" --include="*.js" --include="*.ts" || true')
        if success and output.strip():
            todo_count = len(output.strip().split('\n'))
            if todo_count > 100:
                self._record_pattern(Pattern(
                    id="high-todo-count",
                    type="maintenance",
                    description=f"High TODO count detected ({todo_count} items)",
                    occurrences=todo_count,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["code-analysis"],
                    solutions=[{"description": "Address technical debt systematically", "success_rate": 0.8}],
                    predictors=["maintenance-needed", "tech-debt"]
                ))
    
    def _record_pattern(self, pattern: Pattern) -> None:
        """Record a new pattern or update existing one"""
        if pattern.id in self.patterns:
            existing = self.patterns[pattern.id]
            existing.occurrences += pattern.occurrences
            existing.last_seen = datetime.now()
        else:
            self.patterns[pattern.id] = pattern
    
    def load_historical_patterns(self) -> None:
        """Load historical patterns from previous runs"""
        history_file = self.patterns_dir / "discovered.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        for pattern_data in data:
                            pattern = Pattern(
                                id=pattern_data['id'],
                                type=pattern_data['type'],
                                description=pattern_data['description'],
                                occurrences=pattern_data['occurrences'],
                                first_seen=datetime.fromisoformat(pattern_data['first_seen']),
                                last_seen=datetime.fromisoformat(pattern_data['last_seen']),
                                context=pattern_data['context'],
                                solutions=pattern_data['solutions'],
                                predictors=pattern_data['predictors']
                            )
                            self.patterns[pattern.id] = pattern
                
                print(f"        📚 Loaded {len(self.patterns)} historical patterns")
            except Exception as e:
                print(f"        ⚠️  Could not load patterns: {e}")
    
    def save_patterns(self) -> None:
        """Save discovered patterns"""
        if not self.patterns:
            return
            
        patterns_file = self.patterns_dir / "discovered.json"
        
        try:
            patterns_data = []
            for pattern in self.patterns.values():
                patterns_data.append({
                    'id': pattern.id,
                    'type': pattern.type,
                    'description': pattern.description,
                    'occurrences': pattern.occurrences,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat(),
                    'context': pattern.context,
                    'solutions': pattern.solutions,
                    'predictors': pattern.predictors
                })
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
                
            print(f"        💾 Saved {len(patterns_data)} patterns")
        except Exception as e:
            print(f"        ⚠️  Could not save patterns: {e}")
        
    def get_patterns(self) -> Dict:
        """Get discovered patterns"""
        return self.patterns