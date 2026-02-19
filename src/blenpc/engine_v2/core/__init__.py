"""
BlenPC Engine V2 Core Modules

Pure, immutable, deterministic engine core.
"""

from .grid_state import GridState, Cell, ObjectId
from .collision_engine import detect_collision, check_overlap
from .validation_engine import validate_placement, validate_footprint_shape, validate_cell_coordinates
from .placement_engine import place_object, remove_object, move_object, place_multiple

__all__ = [
    # Grid State
    "GridState",
    "Cell",
    "ObjectId",
    # Collision
    "detect_collision",
    "check_overlap",
    # Validation
    "validate_placement",
    "validate_footprint_shape",
    "validate_cell_coordinates",
    # Placement
    "place_object",
    "remove_object",
    "move_object",
    "place_multiple",
]
