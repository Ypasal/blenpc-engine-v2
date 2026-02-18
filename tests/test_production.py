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

def test_wall_production():
    input_data = {
        "command": "create_wall",
        "asset": {
            "name": "EngineeredWall_V1",
            "dimensions": {"width": 4.0},
            "tags": ["arch_wall", "mat_concrete", "style_modern"]
        }
    }
    
    input_file = os.path.join(project_root, "prod_input.json")
    output_file = os.path.join(project_root, "prod_output.json")

    with open(input_file, "w") as f:
        json.dump(input_data, f)
        
    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", os.path.join(project_root, "run_command.py"),
        "--", input_file, output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    assert result.returncode == 0
    
    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        output_data = json.load(f)
        assert output_data["status"] == "success"
        
    # Check if files were created
    blend_file_path = os.path.join(LIBRARY_DIR, "EngineeredWall_V1.blend")
    assert os.path.exists(blend_file_path)
    
    # Check inventory
    inventory_path = os.path.join(REGISTRY_DIR, "inventory.json")
    with open(inventory_path, "r") as f:
        inventory = json.load(f)
        assert "EngineeredWall_V1" in inventory["assets"]
        assert "mat_concrete" in inventory["assets"]["EngineeredWall_V1"]["tags"]

    # Cleanup
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)
    if os.path.exists(blend_file_path): os.remove(blend_file_path)
    if os.path.exists(os.path.join(REGISTRY_DIR, ".inventory.lock")): os.remove(os.path.join(REGISTRY_DIR, ".inventory.lock"))
