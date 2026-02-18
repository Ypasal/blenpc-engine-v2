import json
import subprocess
import os
import pytest

def test_wall_production():
    input_data = {
        "command": "create_wall",
        "asset": {
            "name": "EngineeredWall_V1",
            "dimensions": {"width": 4.0},
            "tags": ["arch_wall", "mat_concrete", "style_modern"]
        }
    }
    
    with open("prod_input.json", "w") as f:
        json.dump(input_data, f)
        
    cmd = [
        "/home/ubuntu/blender5/blender",
        "--background",
        "--python", "run_command.py",
        "--", "prod_input.json", "prod_output.json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    assert os.path.exists("prod_output.json")
    with open("prod_output.json", "r") as f:
        output_data = json.load(f)
        assert output_data["status"] == "success"
        
    # Check if files were created
    assert os.path.exists("_library/EngineeredWall_V1.blend")
    
    # Check inventory
    with open("_registry/inventory.json", "r") as f:
        inventory = json.load(f)
        assert "EngineeredWall_V1" in inventory["assets"]
        assert "mat_concrete" in inventory["assets"]["EngineeredWall_V1"]["tags"]

    # Cleanup
    if os.path.exists("prod_input.json"): os.remove("prod_input.json")
    if os.path.exists("prod_output.json"): os.remove("prod_output.json")
