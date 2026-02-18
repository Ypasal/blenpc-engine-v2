import json
import os
from typing import List, Dict, Optional, Tuple

# Use absolute import from the project root
from config import INVENTORY_FILE

def get_aabb(obj) -> Dict[str, List[float]]:
    """Calculate Axis-Aligned Bounding Box for a Blender object."""
    import numpy as np
    # Local coordinates of the bounding box corners
    bbox_corners = [obj.matrix_world @ np.array(v) for v in obj.bound_box]
    bbox_corners = np.array(bbox_corners)
    
    min_coords = bbox_corners.min(axis=0).tolist()
    max_coords = bbox_corners.max(axis=0).tolist()
    
    return {
        "min": min_coords,
        "max": max_coords
    }

def find_asset(tags: List[str]) -> Optional[Dict]:
    """Find an asset in the inventory that matches all provided tags."""
    if not os.path.exists(INVENTORY_FILE):
        return None
        
    with open(INVENTORY_FILE, "r") as f:
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
