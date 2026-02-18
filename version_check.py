import bpy
import sys

def check_blender_5_0_api():
    print(f"Checking Blender version: {bpy.app.version_string}")
    
    # 1. Basic Version Check
    if bpy.app.version < (5, 0, 0):
        print("ERROR: This project requires Blender 5.0.1+")
        return False
        
    # 2. Asset Mark API Check (potential changes in 5.0)
    try:
        # Check if asset_mark exists on an ID object
        test_mesh = bpy.data.meshes.new("APITest")
        if hasattr(test_mesh, "asset_mark"):
            print("✓ asset_mark API is present")
        else:
            print("! asset_mark API might have changed or is missing")
    except Exception as e:
        print(f"! Error checking asset_mark: {e}")

    # 3. Library Preview API Check
    try:
        if hasattr(bpy.ops.ed, "lib_id_generate_preview"):
            print("✓ lib_id_generate_preview operator is present")
        else:
            print("! lib_id_generate_preview operator is missing")
    except Exception as e:
        print(f"! Error checking preview operator: {e}")

    # 4. Collection API Check (the one we fixed earlier)
    try:
        if hasattr(bpy.context.scene, "collection"):
            print("✓ scene.collection API is present")
        else:
            print("! scene.collection API is missing")
    except Exception as e:
        print(f"! Error checking collection API: {e}")

    return True

if __name__ == "__main__":
    success = check_blender_5_0_api()
    sys.exit(0 if success else 1)
