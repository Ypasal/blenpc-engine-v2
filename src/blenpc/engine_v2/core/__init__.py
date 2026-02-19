"""
BlenPC Engine V2 Core Modules

Pure, immutable, deterministic engine core.
"""

# Grid State
from .grid_state import GridState, Cell, ObjectId

# Collision
from .collision_engine import detect_collision, check_overlap

# Validation
from .validation_engine import (
    validate_placement,
    validate_footprint_shape,
    validate_cell_coordinates
)

# Placement
from .placement_engine import (
    place_object,
    remove_object,
    move_object,
    place_multiple
)

# State Management
from .state_diff import GridDiff, compute_diff, invert_diff, StateHistory
from .state_machine import Engine

# Analysis Layer
from .room_detection import detect_rooms, get_room_stats, find_room_at_cell
from .structural_graph import (
    build_structural_graph,
    find_connected_components,
    get_graph_stats,
    find_neighbors,
    is_connected,
    get_object_degree
)

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
    # State Management
    "GridDiff",
    "compute_diff",
    "invert_diff",
    "StateHistory",
    "Engine",
    # Analysis Layer
    "detect_rooms",
    "get_room_stats",
    "find_room_at_cell",
    "build_structural_graph",
    "find_connected_components",
    "get_graph_stats",
    "find_neighbors",
    "is_connected",
    "get_object_degree",
]
