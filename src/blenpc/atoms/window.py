"""
Modular Window System - 3-part anatomy with dual material glass for BlenPC v5.2.0

Window Anatomy:
- frame_outer   → outer frame (weather-resistant material)
- frame_inner   → inner frame (interior material)
- glass_pane    → glass with separate inner/outer materials
- [sill_ext]    → optional external sill (sloped for water drainage)
- [sill_int]    → optional internal sill

Slot System:
- wall_interface → connects to wall opening_slot
- blind_slot     → curtain/blind attachment
- latch_slot     → window handle/latch
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json

try:
    import bpy
    import bmesh
except ImportError:
    bpy = None
    bmesh = None

from ..engine.grid_pos import GridPos, meters_to_units
from ..engine.grid_object import GridObjectMixin
from .. import config


@dataclass
class WindowData(GridObjectMixin):
    """
    Complete window data structure implementing IGridObject.
    
    Attributes:
        name: Unique window identifier
        grid_pos: Position in grid space
        grid_size: Size in grid units
        snap_mode: Snap mode used
        style: Window style ("small" | "standard" | "large" | "panoramic")
        frame_material: Frame material ("wood" | "aluminum" | "pvc")
        frame_color: Optional frame color [R, G, B]
        glass_inner: Inner glass material type
        glass_outer: Outer glass material type
        has_sill: Whether to include sills
        parts: Dict of window part names to mesh data
        slots: List of slot definitions
        tags: Classification tags
        meta: Additional metadata
    """
    name: str
    grid_pos: GridPos
    grid_size: Tuple[int, int, int]
    snap_mode: str
    style: str
    frame_material: str
    frame_color: Optional[Tuple[float, float, float]]
    glass_inner: str
    glass_outer: str
    has_sill: bool
    parts: Dict[str, Dict] = field(default_factory=dict)
    slots: List[Dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)


# Glass material definitions
GLASS_MATERIALS = {
    "transparent": {
        "alpha": 0.05,
        "ior": 1.45,
        "roughness": 0.0,
        "color": [0.9, 0.9, 0.9]
    },
    "mirror": {
        "alpha": 0.0,
        "metallic": 1.0,
        "roughness": 0.0,
        "color": [0.8, 0.8, 0.8]
    },
    "frosted": {
        "alpha": 0.3,
        "roughness": 0.6,
        "color": [0.9, 0.9, 0.9]
    },
    "tinted": {
        "alpha": 0.2,
        "roughness": 0.1,
        "color": [0.1, 0.1, 0.15]
    }
}


def build_window(
    style: str = "standard",
    frame_material: str = "wood",
    frame_color: Optional[Tuple[float, float, float]] = None,
    glass_inner: str = "transparent",
    glass_outer: str = "transparent",
    has_sill: bool = True,
    name: str = "window",
    position: Optional[Tuple[float, float, float]] = None
) -> WindowData:
    """
    Build a modular window with 3-part anatomy and dual material glass.
    
    Args:
        style: Window style ("small" | "standard" | "large" | "panoramic")
        frame_material: Frame material ("wood" | "aluminum" | "pvc")
        frame_color: Optional frame color [R, G, B]
        glass_inner: Inner glass material ("transparent" | "mirror" | "frosted" | "tinted")
        glass_outer: Outer glass material
        has_sill: Whether to include sills
        name: Window identifier
        position: Optional position in meters (x, y, z)
    
    Returns:
        WindowData object with parts and slots
    
    Example:
        >>> window = build_window(
        ...     style="standard",
        ...     frame_material="wood",
        ...     glass_inner="transparent",
        ...     glass_outer="mirror"
        ... )
        >>> len(window.parts)
        3  # frame_outer, frame_inner, glass_pane (+ optional sills)
    """
    # Validate inputs
    if style not in config.WINDOW_STANDARDS:
        raise ValueError(f"Invalid window style: {style}. Valid: {list(config.WINDOW_STANDARDS.keys())}")
    
    valid_frame_materials = ["wood", "aluminum", "pvc"]
    if frame_material not in valid_frame_materials:
        raise ValueError(f"Invalid frame material: {frame_material}. Valid: {valid_frame_materials}")
    
    if glass_inner not in GLASS_MATERIALS:
        raise ValueError(f"Invalid glass_inner: {glass_inner}. Valid: {list(GLASS_MATERIALS.keys())}")
    
    if glass_outer not in GLASS_MATERIALS:
        raise ValueError(f"Invalid glass_outer: {glass_outer}. Valid: {list(GLASS_MATERIALS.keys())}")
    
    # Get standard dimensions
    dims = config.WINDOW_STANDARDS[style]
    width = dims["w"]
    height = dims["h"]
    sill_height = dims["sill"]
    
    # Window constants
    FRAME_THICKNESS = 0.05  # 5cm frame thickness
    GLASS_THICKNESS = 0.02  # 2cm glass thickness (double glazing)
    FRAME_DEPTH = 0.15      # 15cm frame depth
    SILL_DEPTH = 0.20       # 20cm sill depth
    SILL_THICKNESS = 0.03   # 3cm sill thickness
    
    # Convert to grid coordinates
    if position is None:
        position = (0.0, 0.0, sill_height)
    
    grid_pos = GridPos.from_meters(*position, snap="meso")
    width_units = meters_to_units(width)
    height_units = meters_to_units(height)
    depth_units = meters_to_units(FRAME_DEPTH)
    
    grid_size = (width_units, depth_units, height_units)
    
    # Build parts
    parts = {
        "frame_outer": {
            "type": "frame",
            "position": [0.0, 0.0, 0.0],
            "size": [width, FRAME_DEPTH, height],
            "material": frame_material,
            "color": frame_color,
            "layer": "outer"
        },
        "frame_inner": {
            "type": "frame",
            "position": [FRAME_THICKNESS, FRAME_THICKNESS, FRAME_THICKNESS],
            "size": [width - 2 * FRAME_THICKNESS, FRAME_DEPTH - 2 * FRAME_THICKNESS, height - 2 * FRAME_THICKNESS],
            "material": frame_material,
            "color": frame_color,
            "layer": "inner"
        },
        "glass_pane": {
            "type": "glass",
            "position": [FRAME_THICKNESS, FRAME_DEPTH / 2, FRAME_THICKNESS],
            "size": [width - 2 * FRAME_THICKNESS, GLASS_THICKNESS, height - 2 * FRAME_THICKNESS],
            "material_inner": glass_inner,
            "material_outer": glass_outer,
            "properties_inner": GLASS_MATERIALS[glass_inner],
            "properties_outer": GLASS_MATERIALS[glass_outer]
        }
    }
    
    # Add sills if requested
    if has_sill:
        parts["sill_ext"] = {
            "type": "sill",
            "position": [0.0, -SILL_DEPTH / 2, -SILL_THICKNESS],
            "size": [width, SILL_DEPTH, SILL_THICKNESS],
            "material": frame_material,
            "slope": 5.0,  # degrees for water drainage
            "layer": "exterior"
        }
        parts["sill_int"] = {
            "type": "sill",
            "position": [0.0, FRAME_DEPTH, -SILL_THICKNESS],
            "size": [width, SILL_DEPTH / 2, SILL_THICKNESS],
            "material": frame_material,
            "slope": 0.0,
            "layer": "interior"
        }
    
    # Build slots
    slots = []
    
    # 1. Wall interface slot (connects to wall opening)
    wall_interface_slot = {
        "id": "wall_interface",
        "type": "window_opening",
        "grid_pos": GridPos(
            width_units // 2,
            depth_units // 2,
            height_units // 2
        ),
        "pos_meters": (width / 2, FRAME_DEPTH / 2, sill_height + height / 2),
        "size_meters": (width, height),
        "sill_height": sill_height,
        "required": True,
        "occupied": False
    }
    slots.append(wall_interface_slot)
    
    # 2. Blind/curtain slot
    blind_slot = {
        "id": "blind",
        "type": "window_blind",
        "grid_pos": GridPos.from_meters(width / 2, FRAME_DEPTH + 0.05, height - 0.1, snap="micro"),
        "pos_meters": (width / 2, FRAME_DEPTH + 0.05, height - 0.1),
        "size_meters": (width, height),
        "required": False,
        "occupied": False
    }
    slots.append(blind_slot)
    
    # 3. Latch/handle slot
    latch_slot = {
        "id": "latch",
        "type": "window_latch",
        "grid_pos": GridPos.from_meters(width / 2, FRAME_DEPTH / 2, height / 2, snap="micro"),
        "pos_meters": (width / 2, FRAME_DEPTH / 2, height / 2),
        "size_meters": (0.05, 0.05),
        "required": False,
        "occupied": False
    }
    slots.append(latch_slot)
    
    # Build tags
    tags = [
        "arch_window",
        f"window_{style}",
        f"mat_{frame_material}",
        f"glass_inner_{glass_inner}",
        f"glass_outer_{glass_outer}",
        f"size_{width}m",
        "modular_v2"
    ]
    
    # Build metadata
    meta = {
        "width_m": width,
        "height_m": height,
        "sill_height_m": sill_height,
        "style": style,
        "frame_material": frame_material,
        "frame_color": frame_color,
        "glass_inner": glass_inner,
        "glass_outer": glass_outer,
        "has_sill": has_sill,
        "frame_thickness": FRAME_THICKNESS,
        "glass_thickness": GLASS_THICKNESS,
        "part_count": len(parts),
        "slot_count": len(slots),
        "aabb": {
            "min": [0.0, -SILL_DEPTH / 2 if has_sill else 0.0, -SILL_THICKNESS if has_sill else 0.0],
            "max": [width, FRAME_DEPTH + SILL_DEPTH / 2 if has_sill else FRAME_DEPTH, height]
        }
    }
    
    return WindowData(
        name=name,
        grid_pos=grid_pos,
        grid_size=grid_size,
        snap_mode="meso",
        style=style,
        frame_material=frame_material,
        frame_color=frame_color,
        glass_inner=glass_inner,
        glass_outer=glass_outer,
        has_sill=has_sill,
        parts=parts,
        slots=slots,
        tags=tags,
        meta=meta
    )


def generate_window_mesh(window_data: WindowData) -> Optional[object]:
    """
    Generate Blender mesh from window data.
    
    Args:
        window_data: WindowData object from build_window()
    
    Returns:
        Blender object with mesh, or None if bpy not available
    
    Note:
        Creates separate objects for each part, grouped under parent.
    """
    if not bpy:
        raise ImportError("Blender 'bpy' module required for mesh generation")
    
    # Create parent empty
    parent = bpy.data.objects.new(window_data.name, None)
    parent.empty_display_type = 'PLAIN_AXES'
    parent.empty_display_size = 0.1
    
    if bpy.context.scene.collection:
        bpy.context.scene.collection.objects.link(parent)
    
    # Generate mesh for each part
    for part_name, part_data in window_data.parts.items():
        mesh = bpy.data.meshes.new(f"{window_data.name}_{part_name}")
        obj = bpy.data.objects.new(f"{window_data.name}_{part_name}", mesh)
        
        if bpy.context.scene.collection:
            bpy.context.scene.collection.objects.link(obj)
        
        # Parent to main object
        obj.parent = parent
        
        # Create box geometry
        bm = bmesh.new()
        
        pos = part_data["position"]
        size = part_data["size"]
        
        # Create cube and scale
        bmesh.ops.create_cube(bm, size=1.0)
        
        # Scale and position
        for v in bm.verts:
            v.co.x = v.co.x * size[0] / 2 + pos[0] + size[0] / 2
            v.co.y = v.co.y * size[1] / 2 + pos[1] + size[1] / 2
            v.co.z = v.co.z * size[2] / 2 + pos[2] + size[2] / 2
        
        bm.to_mesh(mesh)
        bm.free()
        
        # Store part metadata
        obj["part_type"] = part_data["type"]
        if "material" in part_data:
            obj["material_type"] = part_data["material"]
    
    # Store metadata in parent
    parent["window_data"] = json.dumps({
        "style": window_data.style,
        "frame_material": window_data.frame_material,
        "glass_inner": window_data.glass_inner,
        "glass_outer": window_data.glass_outer,
        "parts": len(window_data.parts),
        "slots": len(window_data.slots)
    })
    
    if window_data.slots:
        # Convert GridPos to serializable format
        serializable_slots = []
        for slot in window_data.slots:
            slot_copy = slot.copy()
            if "grid_pos" in slot_copy and hasattr(slot_copy["grid_pos"], "to_tuple"):
                slot_copy["grid_pos"] = slot_copy["grid_pos"].to_tuple()
            serializable_slots.append(slot_copy)
        parent["slots_json"] = json.dumps(serializable_slots)
    
    # Mark as asset
    parent.asset_mark()
    
    return parent


def window_to_json(window_data: WindowData) -> str:
    """
    Serialize window data to JSON.
    
    Args:
        window_data: WindowData object
    
    Returns:
        JSON string representation
    """
    # Convert slots to serializable format
    serializable_slots = []
    for slot in window_data.slots:
        slot_copy = slot.copy()
        if "grid_pos" in slot_copy and hasattr(slot_copy["grid_pos"], "to_tuple"):
            slot_copy["grid_pos"] = slot_copy["grid_pos"].to_tuple()
        serializable_slots.append(slot_copy)
    
    data = {
        "name": window_data.name,
        "grid_pos": window_data.grid_pos.to_tuple(),
        "grid_size": window_data.grid_size,
        "snap_mode": window_data.snap_mode,
        "style": window_data.style,
        "frame_material": window_data.frame_material,
        "frame_color": window_data.frame_color,
        "glass_inner": window_data.glass_inner,
        "glass_outer": window_data.glass_outer,
        "has_sill": window_data.has_sill,
        "parts": window_data.parts,
        "slots": serializable_slots,
        "tags": window_data.tags,
        "meta": window_data.meta
    }
    return json.dumps(data, indent=2)
