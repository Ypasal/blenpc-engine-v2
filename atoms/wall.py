import math
import hashlib
import struct
import bpy
import bmesh
from typing import List, Tuple, Dict

# Use absolute import from the project root
from config import PHI, STORY_HEIGHT, WALL_THICKNESS_BASE

def make_rng(seed: int, subsystem: str):
    """Create a deterministic RNG for a specific subsystem."""
    h = hashlib.sha256(f"{seed}:{subsystem}".encode()).digest()
    sub_seed = struct.unpack('<Q', h[:8])[0]
    import random
    return random.Random(sub_seed)

def golden_split(length: float, rng) -> float:
    """Split a length using the Golden Ratio with slight deterministic variation."""
    base_split = length / PHI
    variation = (rng.random() - 0.5) * 0.1 * base_split
    return base_split + variation

def check_manifold(bm) -> bool:
    """Verify if the mesh is a manifold using Euler's Formula: V - E + F = 2."""
    v = len(bm.verts)
    e = len(bm.edges)
    f = len(bm.faces)
    return (v - e + f) == 2

def create_basic_wall_mesh(name: str, length: float, height: float = STORY_HEIGHT, thickness: float = WALL_THICKNESS_BASE):
    """Create a manifold wall mesh in Blender."""
    # Clear existing data for a clean start in headless
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    # Create a cube-based wall
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale to dimensions
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= thickness
        v.co.z *= height
        # Move to sit on ground and start at origin
        v.co.z += height / 2
        v.co.x += length / 2
        
    if not check_manifold(bm):
        bm.free()
        raise Exception(f"Mesh generation for {name} failed manifold check")
        
    bm.to_mesh(mesh)
    bm.free()
    
    # Blender 5.0.1 Asset Marking
    obj.asset_mark()
    
    # In Blender 5.0, the preview generation API might be more sensitive to context
    try:
        if hasattr(bpy.ops.ed, "lib_id_generate_preview"):
            # Trying a simpler call without manual context override first
            bpy.ops.ed.lib_id_generate_preview()
    except Exception as e:
        print(f"Warning: Could not generate preview: {e}")
        
    return obj

def calculate_roof_trig(width: float, pitch_deg: float = 35.0) -> Dict[str, float]:
    """Calculate roof geometry using trigonometry."""
    pitch_rad = math.radians(pitch_deg)
    height = (width / 2) * math.tan(pitch_rad)
    slope_length = (width / 2) / math.cos(pitch_rad)
    
    return {
        "height": height,
        "slope_length": slope_length,
        "pitch_deg": pitch_deg
    }
