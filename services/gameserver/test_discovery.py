#!/usr/bin/env python3
"""
Simple test discovery script for VS Code.
This script helps VS Code discover test files without needing full dependencies.
"""

import os
import ast
import sys
from pathlib import Path

def find_test_files(directory):
    """Find all test files in the given directory."""
    test_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    return test_files

def extract_test_functions(file_path):
    """Extract test function names from a Python file."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        test_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) and child.name.startswith('test_'):
                        test_functions.append(f"{node.name}::{child.name}")
        
        return test_functions
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def main():
    """Main discovery function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--collect-only':
        print("Test discovery for VS Code:")
        print("=" * 50)
        
        tests_dir = Path(__file__).parent / 'tests'
        if tests_dir.exists():
            test_files = find_test_files(str(tests_dir))
            
            for test_file in test_files:
                rel_path = os.path.relpath(test_file, str(tests_dir.parent))
                print(f"\n📁 {rel_path}")
                
                test_functions = extract_test_functions(test_file)
                for func in test_functions:
                    print(f"  ✅ {func}")
                    
            print(f"\n📊 Found {len(test_files)} test files with {sum(len(extract_test_functions(f)) for f in test_files)} test functions")
        else:
            print("No tests directory found")
    else:
        # For actual test execution, delegate to container
        os.system(f"cd .. && docker-compose exec -T gameserver poetry run pytest {' '.join(sys.argv[1:])}")

if __name__ == "__main__":
    main()