"""
validation_engine.py - Placement Validation Rules

Design Principles:
- Pure functions (no side effects)
- Raises exceptions on validation failure
- No collision logic (handled by collision_engine)
- No placement logic (handled by placement_engine)

Validation Rules:
1. Object ID cannot be empty
2. Footprint cannot be empty
3. Footprint must be within bounds (if bounds specified)
"""

from typing import FrozenSet, Tuple
from .grid_state import GridState, Cell


def validate_placement(
    object_id: str,
    footprint: FrozenSet[Cell],
    grid: GridState,
    bounds: Tuple[int, int, int] | None = None
) -> None:
    """
    Validate placement parameters.
    
    Args:
        object_id: Unique identifier for the object
        footprint: Set of cells the object will occupy
        grid: Current grid state (for future validation rules)
        bounds: Optional boundary limits (max_x, max_y, max_z)
    
    Raises:
        ValueError: If validation fails
    
    Example:
        >>> validate_placement("wall_01", frozenset({(0,0,0)}), GridState.empty())
        # No exception
        
        >>> validate_placement("", frozenset({(0,0,0)}), GridState.empty())
        ValueError: object_id cannot be empty
    
    Notes:
        - Does not check collision (use collision_engine)
        - Does not modify grid
        - Deterministic
    """
    # Rule 1: Object ID must not be empty
    if not object_id or not object_id.strip():
        raise ValueError("object_id cannot be empty")
    
    # Rule 2: Footprint must not be empty
    if not footprint:
        raise ValueError("footprint cannot be empty")
    
    # Rule 3: Boundary validation (if bounds specified)
    if bounds:
        max_x, max_y, max_z = bounds
        for x, y, z in footprint:
            if not (0 <= x < max_x and 0 <= y < max_y and 0 <= z < max_z):
                raise ValueError(
                    f"Cell ({x}, {y}, {z}) is out of bounds. "
                    f"Bounds: (0-{max_x}, 0-{max_y}, 0-{max_z})"
                )


def validate_footprint_shape(
    footprint: FrozenSet[Cell],
    min_size: int = 1,
    max_size: int | None = None
) -> None:
    """
    Validate footprint size constraints.
    
    Args:
        footprint: Set of cells to validate
        min_size: Minimum number of cells
        max_size: Maximum number of cells (None = unlimited)
    
    Raises:
        ValueError: If footprint size is invalid
    
    Example:
        >>> fp = frozenset({(0,0,0), (1,0,0)})
        >>> validate_footprint_shape(fp, min_size=1, max_size=10)
        # No exception
        
        >>> validate_footprint_shape(fp, min_size=5)
        ValueError: Footprint too small
    """
    size = len(footprint)
    
    if size < min_size:
        raise ValueError(
            f"Footprint too small: {size} cells (minimum: {min_size})"
        )
    
    if max_size is not None and size > max_size:
        raise ValueError(
            f"Footprint too large: {size} cells (maximum: {max_size})"
        )


def validate_cell_coordinates(
    cell: Cell,
    allow_negative: bool = False
) -> None:
    """
    Validate individual cell coordinates.
    
    Args:
        cell: Cell tuple (x, y, z)
        allow_negative: Whether negative coordinates are allowed
    
    Raises:
        ValueError: If coordinates are invalid
    
    Example:
        >>> validate_cell_coordinates((0, 0, 0))
        # No exception
        
        >>> validate_cell_coordinates((-1, 0, 0))
        ValueError: Negative coordinates not allowed
    """
    x, y, z = cell
    
    if not allow_negative:
        if x < 0 or y < 0 or z < 0:
            raise ValueError(
                f"Negative coordinates not allowed: ({x}, {y}, {z})"
            )
