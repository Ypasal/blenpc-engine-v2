import math
import hashlib
import struct
import json
import os
try:
    import bpy
    import bmesh
except ImportError:
    bpy = None
    bmesh = None
    
from typing import List, Tuple, Dict, Optional

# Use safe import from the project root
try:
    import config
except ImportError:
    from .. import config

def make_rng(seed: int, subsystem: str):
    """Create a deterministic RNG for a specific subsystem."""
    h = hashlib.sha256(f"{seed}:{subsystem}".encode()).digest()
    sub_seed = struct.unpack('<Q', h[:8])[0]
    import random
    return random.Random(sub_seed)

def golden_split(length: float, rng) -> float:
    """Split a length using the Golden Ratio with slight deterministic variation."""
    # Standard split at 1/PHI or (1 - 1/PHI)
    split_point = length / config.PHI
    # Add variation based on RNG to avoid perfect repetition while maintaining aesthetics
    variation = (rng.random() - 0.5) * config.GOLDEN_RATIO_VARIATION * length
    final_split = split_point + variation
    
    # Snap to GRID_UNIT for modularity
    return round(final_split / config.GRID_UNIT) * config.GRID_UNIT

def check_manifold(bm) -> bool:
    """Verify if the mesh is a manifold using Euler's Formula: V - E + F = 2."""
    if not bm: return False
    v = len(bm.verts)
    e = len(bm.edges)
    f = len(bm.faces)
    # Simple check for closed genus-0 mesh
    return (v - e + f) == 2

def validate_slot(slot: Dict, slot_types_file: str = "_registry/slot_types.json") -> bool:
    """Validate slot data against registry schema."""
    if not os.path.exists(slot_types_file):
        return True  # Skip validation if registry doesn't exist
    
    with open(slot_types_file, 'r') as f:
        slot_types = json.load(f)
    
    slot_type = slot.get("type")
    if slot_type not in slot_types.get("types", {}):
        raise ValueError(f"Unknown slot type: {slot_type}")
    
    # Validate required fields
    required_fields = ["id", "type", "pos", "size"]
    for field in required_fields:
        if field not in slot:
            raise ValueError(f"Missing required field '{field}' in slot")
    
    # Validate pos is 3D coordinate
    if not isinstance(slot["pos"], list) or len(slot["pos"]) != 3:
        raise ValueError(f"Slot 'pos' must be [x, y, z] list")
    
    # Validate size is 2D
    if not isinstance(slot["size"], list) or len(slot["size"]) != 2:
        raise ValueError(f"Slot 'size' must be [width, height] list")
    
    return True

def create_engineered_wall(name: str, length: float, seed: int = 0):
    """Create a wall with mathematically placed slots for openings."""
    if not bpy:
        raise ImportError("Blender 'bpy' module is required for this function.")
        
    rng = make_rng(seed, "wall_slots")
    
    # Clear existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale to dimensions
    thickness = config.WALL_THICKNESS_BASE
    height = config.STORY_HEIGHT
    
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= thickness
        v.co.z *= height
        v.co.z += height / 2
        v.co.x += length / 2
        
    if not check_manifold(bm):
        bm.free()
        raise Exception(f"Manifold check failed for {name}")
        
    bm.to_mesh(mesh)
    bm.free()
    
    # Define Slots (Mathematical placement)
    # Use Golden Ratio to find a primary 'feature' spot (e.g., a window)
    primary_slot_x = golden_split(length, rng)
    
    # Metadata for slots
    slots = [
        {
            "id": "main_opening",
            "type": "window_opening",
            "pos": [primary_slot_x, 0, config.WINDOW_SILL_HEIGHT_DEFAULT],
            "size": [config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT]
        }
    ]
    
    # Validate slots
    for slot in slots:
        validate_slot(slot)
    
    # Mark as asset and store metadata
    obj.asset_mark()
    obj["slots_json"] = json.dumps(slots)
    
    return obj, slots

def calculate_roof_trig(width: float, pitch_deg: float = None) -> Dict[str, float]:
    """Calculate roof geometry using trigonometry."""
    if pitch_deg is None:
        pitch_deg = config.DEFAULT_ROOF_PITCH
        
    pitch_rad = math.radians(pitch_deg)
    height = (width / 2) * math.tan(pitch_rad)
    slope_length = (width / 2) / math.cos(pitch_rad)
    
    return {
        "height": height,
        "slope_length": slope_length,
        "pitch_deg": pitch_deg
    }
