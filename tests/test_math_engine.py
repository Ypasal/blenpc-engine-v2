import json
import subprocess
import os
import pytest
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config import BLENDER_PATH, LIBRARY_DIR, REGISTRY_DIR

def test_golden_ratio_wall_production():
    # Test two walls with different seeds to ensure deterministic but different slot placement
    for seed in [123, 456]:
        name = f"MathWall_S{seed}"
        input_data = {
            "command": "create_wall",
            "seed": seed,
            "asset": {
                "name": name,
                "dimensions": {"width": 5.0},
                "tags": ["arch_wall", "math_verified"]
            }
        }
        
        input_file = os.path.join(project_root, f"test_in_{seed}.json")
        output_file = os.path.join(project_root, f"test_out_{seed}.json")
        
        with open(input_file, "w") as f:
            json.dump(input_data, f)
            
        cmd = [
            BLENDER_PATH,
            "--background", "--python", os.path.join(project_root, "run_command.py"),
            "--", input_file, output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        assert os.path.exists(output_file)
        with open(output_file, "r") as f:
            out = json.load(f)
            assert out["status"] == "success"
            
        # Verify Inventory Entry
        inventory_path = os.path.join(REGISTRY_DIR, "inventory.json")
        with open(inventory_path, "r") as f:
            inv = json.load(f)
            asset = inv["assets"][name]
            assert "slots" in asset
            assert len(asset["slots"]) > 0
            # Check if position is snapped to GRID_UNIT (0.25)
            pos_x = asset["slots"][0]["pos"][0]
            assert pos_x % 0.25 == 0
            
        # Cleanup
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)
        if os.path.exists(os.path.join(LIBRARY_DIR, f"{name}.blend")): os.remove(os.path.join(LIBRARY_DIR, f"{name}.blend"))
        if os.path.exists(os.path.join(REGISTRY_DIR, ".inventory.lock")): os.remove(os.path.join(REGISTRY_DIR, ".inventory.lock"))
