"""
Metrics Collection Module
=========================

Collects code metrics like lines of code, file counts, etc.
"""

import re
from pathlib import Path
from typing import Dict, List
from .data_structures import CodeMetrics


class MetricsCollector:
    """Collects various code and project metrics"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics = CodeMetrics()
    
    def collect(self) -> CodeMetrics:
        """Collect all metrics"""
        self._count_files()
        self._count_lines()
        self._count_todos()
        self._estimate_test_coverage()
        return self.metrics
    
    def get_metrics(self) -> Dict:
        """Get metrics as dictionary"""
        return {
            'line_count': self.metrics.line_count,
            'python_files': self.metrics.python_files,
            'javascript_files': self.metrics.javascript_files,
            'typescript_files': self.metrics.typescript_files,
            'php_files': self.metrics.php_files,
            'vue_files': self.metrics.vue_files,
            'rust_files': self.metrics.rust_files,
            'go_files': self.metrics.go_files,
            'java_files': self.metrics.java_files,
            'ruby_files': self.metrics.ruby_files,
            'css_files': self.metrics.css_files,
            'scss_files': self.metrics.scss_files,
            'todo_count': self.metrics.todo_count,
            'test_coverage': self.metrics.test_coverage,
            'complexity': self.metrics.complexity,
            'duplicate_count': self.metrics.duplicate_count
        }
    
    def _count_files(self) -> None:
        """Count files by type"""
        file_patterns = {
            'python_files': ['*.py'],
            'javascript_files': ['*.js', '*.jsx'],
            'typescript_files': ['*.ts', '*.tsx'],
            'php_files': ['*.php'],
            'vue_files': ['*.vue'],
            'rust_files': ['*.rs'],
            'go_files': ['*.go'],
            'java_files': ['*.java'],
            'ruby_files': ['*.rb'],
            'css_files': ['*.css'],
            'scss_files': ['*.scss', '*.sass']
        }
        
        for metric_name, patterns in file_patterns.items():
            count = 0
            for pattern in patterns:
                files = list(self.project_root.rglob(pattern))
                # Exclude common build/dependency directories
                files = self._filter_excluded_files(files)
                count += len(files)
            setattr(self.metrics, metric_name, count)
    
    def _filter_excluded_files(self, files: List[Path]) -> List[Path]:
        """Filter out files in excluded directories"""
        excluded_dirs = [
            'node_modules', '.git', 'vendor', 'build', 'dist', 
            '__pycache__', '.venv', 'venv', 'target', '.claude'
        ]
        
        filtered = []
        for file_path in files:
            if not any(excluded in str(file_path) for excluded in excluded_dirs):
                filtered.append(file_path)
        return filtered
    
    def _count_lines(self) -> None:
        """Count total lines of code"""
        patterns = ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.php', '*.vue', '*.rs', '*.go', '*.java', '*.rb', '*.css', '*.scss']
        total_lines = 0
        
        for pattern in patterns:
            files = list(self.project_root.rglob(pattern))
            files = self._filter_excluded_files(files)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    try:
                        # Try with different encoding
                        with open(file_path, 'r', encoding='latin-1') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass  # Skip files we can't read
        
        self.metrics.line_count = total_lines
    
    def _count_todos(self) -> None:
        """Count TODO, FIXME, BUG, HACK comments"""
        patterns = ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.php', '*.vue', '*.rs', '*.go', '*.java', '*.rb']
        todo_count = 0
        
        todo_patterns = [
            r'TODO',
            r'FIXME', 
            r'BUG',
            r'HACK',
            r'XXX'
        ]
        
        for pattern in patterns:
            files = list(self.project_root.rglob(pattern))
            files = self._filter_excluded_files(files)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for todo_pattern in todo_patterns:
                            matches = re.findall(todo_pattern, content, re.IGNORECASE)
                            todo_count += len(matches)
                except:
                    pass  # Skip files we can't read
        
        self.metrics.todo_count = todo_count
    
    def _estimate_test_coverage(self) -> None:
        """Estimate test coverage based on available data"""
        # Try to find coverage reports
        coverage_files = [
            'htmlcov/index.html',
            'coverage.xml',
            '.coverage',
            'coverage/index.html'
        ]
        
        for coverage_file in coverage_files:
            coverage_path = self.project_root / coverage_file
            if coverage_path.exists():
                coverage = self._parse_coverage_file(coverage_path)
                if coverage is not None:
                    self.metrics.test_coverage = coverage
                    return
        
        # Fallback: estimate based on test file ratio
        test_files = list(self.project_root.rglob("*test*.py"))
        test_files.extend(list(self.project_root.rglob("*.test.js")))
        test_files.extend(list(self.project_root.rglob("*.spec.ts")))
        
        source_files = self.metrics.python_files + self.metrics.javascript_files + self.metrics.typescript_files
        
        if source_files > 0:
            # Very rough estimation: if we have 1 test file per 3 source files, assume 60% coverage
            test_ratio = len(test_files) / source_files
            estimated_coverage = min(test_ratio * 180, 100)  # Cap at 100%
            self.metrics.test_coverage = round(estimated_coverage, 1)
    
    def _parse_coverage_file(self, coverage_path: Path) -> float:
        """Parse coverage percentage from coverage file"""
        try:
            if coverage_path.name == 'index.html':
                # Parse HTML coverage report
                content = coverage_path.read_text()
                match = re.search(r'(\d+(?:\.\d+)?)%', content)
                if match:
                    return float(match.group(1))
            elif coverage_path.suffix == '.xml':
                # Parse XML coverage report
                content = coverage_path.read_text()
                match = re.search(r'line-rate="([0-9.]+)"', content)
                if match:
                    return float(match.group(1)) * 100
        except:
            pass
        return None