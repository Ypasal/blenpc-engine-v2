"""
Comprehensive Regression Test Suite for BlenPC v5.2.0

This suite runs all tests and verifies:
1. Grid system integrity
2. Modular wall/door/window generation
3. Composed wall integration
4. Room automation
5. Backward compatibility
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    """Run all tests in the repository."""
    test_files = [
        "tests/test_grid_system.py",
        "tests/test_wall_modular.py",
        "tests/test_door.py",
        "tests/test_composed_wall.py",
        "tests/test_room_automation.py"
    ]
    
    print(f"Running {len(test_files)} test modules...")
    exit_code = pytest.main(test_files + ["-v"])
    return exit_code

if __name__ == "__main__":
    sys.exit(run_all_tests())
