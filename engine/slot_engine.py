import json
import os
from typing import List, Dict, Optional, Tuple

# Use safe import from the project root
try:
    import config
except ImportError:
    from .. import config

def get_aabb(obj) -> Dict[str, List[float]]:
    """Calculate Axis-Aligned Bounding Box for a Blender object."""
    # Get world-space bounding box corners
    bbox_corners = [obj.matrix_world @ v for v in obj.bound_box]
    
    # Calculate min/max for each axis
    min_x = min(v[0] for v in bbox_corners)
    min_y = min(v[1] for v in bbox_corners)
    min_z = min(v[2] for v in bbox_corners)
    
    max_x = max(v[0] for v in bbox_corners)
    max_y = max(v[1] for v in bbox_corners)
    max_z = max(v[2] for v in bbox_corners)
    
    return {
        "min": [min_x, min_y, min_z],
        "max": [max_x, max_y, max_z]
    }

def find_asset(tags: List[str]) -> Optional[Dict]:
    """Find an asset in the inventory that matches all provided tags."""
    if not os.path.exists(config.INVENTORY_FILE):
        return None
        
    with open(config.INVENTORY_FILE, "r") as f:
        inventory = json.load(f)
        
    for asset_id, asset_data in inventory.get("assets", {}).items():
        if all(tag in asset_data.get("tags", []) for tag in tags):
            return asset_data
            
    return None

def place_on_slot(parent_obj, slot_data: Dict, asset_tags: List[str]):
    """Place a matching asset on a specific slot of a parent object."""
    asset_data = find_asset(asset_tags)
    if not asset_data:
        return {"status": "error", "message": f"Asset not found for tags: {asset_tags}"}
        
    return {"status": "success", "asset": asset_data["name"]}
