"""
placement_engine.py - Immutable Placement Engine

Design Principles:
- Pure function (returns new GridState)
- Immutable (never modifies input grid)
- Validates before placing
- Checks collision before placing
- Raises exceptions on failure

Placement Pipeline:
    validate → collision check → new state
"""

from typing import FrozenSet
from .grid_state import GridState, Cell, ObjectId
from .collision_engine import detect_collision
from .validation_engine import validate_placement


def place_object(
    object_id: ObjectId,
    footprint: FrozenSet[Cell],
    grid: GridState,
    bounds: tuple[int, int, int] | None = None
) -> GridState:
    """
    Place an object on the grid, returning a new GridState.
    
    Args:
        object_id: Unique identifier for the object
        footprint: Set of cells the object will occupy
        grid: Current grid state
        bounds: Optional boundary limits (max_x, max_y, max_z)
    
    Returns:
        New GridState with the object placed
    
    Raises:
        ValueError: If validation fails or collision detected
    
    Example:
        >>> grid = GridState.empty()
        >>> footprint = frozenset({(0,0,0), (1,0,0)})
        >>> new_grid = place_object("wall_01", footprint, grid)
        >>> new_grid.is_occupied((0,0,0))
        True
        >>> len(new_grid)
        2
    
    Notes:
        - Original grid is never modified
        - Returns new GridState instance
        - Deterministic (same input → same output)
    
    Complexity:
        O(n) where n = len(footprint)
    """
    # Step 1: Validate placement parameters
    validate_placement(object_id, footprint, grid, bounds)
    
    # Step 2: Check for collision
    if detect_collision(footprint, grid):
        raise ValueError(
            f"Collision detected: object '{object_id}' overlaps with existing objects"
        )
    
    # Step 3: Create new grid state
    new_cells = dict(grid._cells)  # Copy existing cells
    
    for cell in footprint:
        new_cells[cell] = object_id
    
    return GridState(_cells=new_cells)


def remove_object(
    object_id: ObjectId,
    grid: GridState
) -> GridState:
    """
    Remove an object from the grid, returning a new GridState.
    
    Args:
        object_id: ID of the object to remove
        grid: Current grid state
    
    Returns:
        New GridState with the object removed
    
    Raises:
        ValueError: If object not found
    
    Example:
        >>> grid = GridState(_cells={(0,0,0): "wall_01", (1,0,0): "wall_01"})
        >>> new_grid = remove_object("wall_01", grid)
        >>> len(new_grid)
        0
    
    Notes:
        - Original grid is never modified
        - All cells belonging to the object are removed
    """
    if object_id not in grid.object_ids():
        raise ValueError(f"Object '{object_id}' not found in grid")
    
    # Create new cells dict without the object
    new_cells = {
        cell: obj_id
        for cell, obj_id in grid._cells.items()
        if obj_id != object_id
    }
    
    return GridState(_cells=new_cells)


def move_object(
    object_id: ObjectId,
    new_footprint: FrozenSet[Cell],
    grid: GridState,
    bounds: tuple[int, int, int] | None = None
) -> GridState:
    """
    Move an object to a new position.
    
    Equivalent to: remove_object → place_object
    
    Args:
        object_id: ID of the object to move
        new_footprint: New footprint for the object
        grid: Current grid state
        bounds: Optional boundary limits
    
    Returns:
        New GridState with the object moved
    
    Raises:
        ValueError: If object not found, validation fails, or collision detected
    
    Example:
        >>> grid = GridState(_cells={(0,0,0): "wall_01"})
        >>> new_fp = frozenset({(5,0,0)})
        >>> new_grid = move_object("wall_01", new_fp, grid)
        >>> new_grid.is_occupied((0,0,0))
        False
        >>> new_grid.is_occupied((5,0,0))
        True
    """
    # Step 1: Remove object
    grid_without_object = remove_object(object_id, grid)
    
    # Step 2: Place at new location
    return place_object(object_id, new_footprint, grid_without_object, bounds)


def place_multiple(
    placements: list[tuple[ObjectId, FrozenSet[Cell]]],
    grid: GridState,
    bounds: tuple[int, int, int] | None = None
) -> GridState:
    """
    Place multiple objects in sequence.
    
    Args:
        placements: List of (object_id, footprint) tuples
        grid: Starting grid state
        bounds: Optional boundary limits
    
    Returns:
        New GridState with all objects placed
    
    Raises:
        ValueError: If any placement fails
    
    Example:
        >>> grid = GridState.empty()
        >>> placements = [
        ...     ("wall_01", frozenset({(0,0,0)})),
        ...     ("wall_02", frozenset({(5,0,0)})),
        ... ]
        >>> new_grid = place_multiple(placements, grid)
        >>> len(new_grid)
        2
    
    Notes:
        - Placements are applied in order
        - If any placement fails, exception is raised
        - Deterministic (same order → same result)
    """
    current_grid = grid
    
    for object_id, footprint in placements:
        current_grid = place_object(object_id, footprint, current_grid, bounds)
    
    return current_grid
