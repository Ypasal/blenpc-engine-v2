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

def test_full_pipeline_integration():
    fixture_path = os.path.join(project_root, "tests/fixtures/standard_wall.json")
    output_path = os.path.join(project_root, "tests/fixtures/standard_wall_output.json")
    
    # Ensure fixture exists
    assert os.path.exists(fixture_path)
    
    # Run production command
    cmd = [
        BLENDER_PATH,
        "--background", "--python", os.path.join(project_root, "run_command.py"),
        "--", fixture_path, output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    
    # Validate output report
    assert os.path.exists(output_path)
    with open(output_path, "r") as f:
        data = json.load(f)
        assert data["status"] == "success"
        assert "asset_name" in data["result"]
        
    # Validate registry persistence
    inventory_path = os.path.join(REGISTRY_DIR, "inventory.json")
    with open(inventory_path, "r") as f:
        inventory = json.load(f)
        asset_name = data["result"]["asset_name"]
        assert asset_name in inventory["assets"]
        
        asset = inventory["assets"][asset_name]
        assert len(asset["slots"]) > 0
        # Check modularity (GRID_UNIT = 0.25)
        for slot in asset["slots"]:
            assert slot["pos"][0] % 0.25 == 0

    # Validate file existence
    assert os.path.exists(os.path.join(LIBRARY_DIR, f"{asset_name}.blend"))

    # Cleanup output only, keep fixture
    if os.path.exists(output_path): os.remove(output_path)
    if os.path.exists(os.path.join(LIBRARY_DIR, f"{asset_name}.blend")): os.remove(os.path.join(LIBRARY_DIR, f"{asset_name}.blend"))
    if os.path.exists(os.path.join(REGISTRY_DIR, ".inventory.lock")): os.remove(os.path.join(REGISTRY_DIR, ".inventory.lock"))
