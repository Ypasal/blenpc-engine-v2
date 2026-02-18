import sys
import json
import os
import time
import bpy

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Use absolute imports instead of relative ones for the main entry point
from atoms.wall import create_basic_wall_mesh
from engine.inventory_manager import InventoryManager

def run():
    try:
        if '--' in sys.argv:
            args = sys.argv[sys.argv.index('--') + 1:]
            input_file = args[0]
            output_file = args[1]
        else:
            print("Usage: blender --background --python run_command.py -- <input.json> <output.json>")
            sys.exit(1)
    except (ValueError, IndexError):
        print("Usage: blender --background --python run_command.py -- <input.json> <output.json>")
        sys.exit(1)

    if not os.path.exists(input_file):
        result = {"status": "error", "message": f"Input {input_file} not found"}
    else:
        try:
            with open(input_file, 'r') as f:
                command_data = json.load(f)
            
            cmd = command_data.get("command")
            
            if cmd == "create_wall":
                wall_data = command_data.get("asset", {})
                name = wall_data.get("name", "GeneratedWall")
                length = wall_data.get("dimensions", {}).get("width", 2.0)
                
                # Create the actual mesh
                obj = create_basic_wall_mesh(name, length)
                
                # Register in inventory
                asset_info = {
                    "name": name,
                    "tags": wall_data.get("tags", ["arch_wall"]),
                    "dimensions": {"width": length, "height": 3.0, "depth": 0.2},
                    "blend_file": f"_library/{name}.blend"
                }
                InventoryManager.register_asset(asset_info)
                
                # Save blend file
                if not os.path.exists("_library"):
                    os.makedirs("_library")
                lib_path = os.path.join("_library", f"{name}.blend")
                bpy.ops.wm.save_as_mainfile(filepath=lib_path)
                
                result = {
                    "status": "success",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "result": {"asset_name": name, "path": lib_path}
                }
            else:
                result = {"status": "error", "message": f"Unknown command: {cmd}"}
                
        except Exception as e:
            import traceback
            result = {
                "status": "error", 
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run()
