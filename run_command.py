import sys
import json
import os
import time
import bpy
import traceback

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Use absolute imports
from atoms.wall import create_engineered_wall
from engine.inventory_manager import InventoryManager
from config import LIBRARY_DIR, REGISTRY_DIR, INVENTORY_FILE

def run():
    input_file = None
    output_file = None
    try:
        if '--' in sys.argv:
            args = sys.argv[sys.argv.index('--') + 1:]
            if len(args) == 2:
                input_file = args[0]
                output_file = args[1]
            else:
                raise ValueError("Incorrect number of arguments after --")
        else:
            raise ValueError("Missing -- separator for arguments")
    except (ValueError, IndexError) as e:
        result = {"status": "error", "message": f"CLI Argument Error: {e}. Usage: blender --background --python run_command.py -- <input.json> <output.json>"}
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
        sys.exit(1)

    if not os.path.exists(input_file):
        result = {"status": "error", "message": f"Input file not found: {input_file}"}
    else:
        try:
            with open(input_file, 'r') as f:
                command_data = json.load(f)
            
            cmd = command_data.get("command")
            seed = command_data.get("seed", 0)
            
            if cmd == "create_wall":
                wall_data = command_data.get("asset", {})
                name = wall_data.get("name", "GenWall")
                length = wall_data.get("dimensions", {}).get("width", 4.0)
                
                # Create engineered mesh with slots
                obj, slots = create_engineered_wall(name, length, seed)
                
                # Register in inventory with slots
                asset_info = {
                    "name": name,
                    "tags": wall_data.get("tags", ["arch_wall"]),
                    "dimensions": {"width": length, "height": 3.0, "depth": 0.2},
                    "slots": slots,
                    "blend_file": os.path.join(LIBRARY_DIR, f"{name}.blend"),
                    "seed": seed
                }
                InventoryManager.register_asset(asset_info)
                
                # Save
                os.makedirs(LIBRARY_DIR, exist_ok=True)
                lib_path = os.path.join(LIBRARY_DIR, f"{name}.blend")
                bpy.ops.wm.save_as_mainfile(filepath=lib_path)
                
                result = {
                    "status": "success",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "result": {"asset_name": name, "slots_count": len(slots), "blend_file": lib_path}
                }
            else:
                result = {"status": "error", "message": f"Unknown command: {cmd}"}
                
        except Exception as e:
            result = {
                "status": "error", 
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        # If output_file could not be determined, print error to stderr
        print(json.dumps(result, indent=2), file=sys.stderr)

if __name__ == "__main__":
    run()
