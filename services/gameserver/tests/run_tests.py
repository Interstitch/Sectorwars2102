#!/usr/bin/env python3
"""
Helper script to run tests with the correct Python path.
This ensures that imports from the gameserver module work correctly.
"""

import os
import sys
import pytest

# Add the parent directory to the Python path
# This ensures that 'from src import xyz' works correctly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Run pytest with the given arguments
if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv[1:]))
