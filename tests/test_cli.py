import json
import sys
import subprocess
import os
import pytest

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config import BLENDER_PATH

def test_cli_execution():
    input_data = {
        "command": "create_asset",
        "asset": {"name": "test_wall"}
    }
    
    with open("test_input.json", "w") as f:
        json.dump(input_data, f)
        
    # Run via Blender headless
    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", "run_command.py",
        "--", "test_input.json", "test_output.json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    
    assert os.path.exists("test_output.json")
    with open("test_output.json", "r") as f:
        output_data = json.load(f)
        assert output_data["status"] == "success"
        
    # Cleanup
    os.remove("test_input.json")
    os.remove("test_output.json")
