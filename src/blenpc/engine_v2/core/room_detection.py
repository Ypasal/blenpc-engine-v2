"""
room_detection.py - Flood-Fill Based Room Detection

Design Principles:
- Pure function (no side effects)
- Read-only (does not modify grid)
- Z-level separation (2D flood-fill per level)
- O(area) complexity
- Boundary-aware

Algorithm:
    For each z-level:
        1. Find all empty cells
        2. Flood-fill from each unvisited empty cell
        3. Mark connected regions as rooms
        4. Filter out boundary-touching regions (optional)

Room Definition:
    A room is a connected region of empty cells,
    bounded by occupied cells or grid boundaries.
"""

from typing import List, Set, FrozenSet
from collections import deque
from .grid_state import GridState, Cell


def detect_rooms(
    grid: GridState,
    z_level: int = 0,
    min_size: int = 4,
    exclude_boundary_touching: bool = True,
    bounds: tuple[int, int] | None = None
) -> List[FrozenSet[Cell]]:
    """
    Detect rooms on a specific z-level using flood-fill.
    
    Args:
        grid: Current grid state
        z_level: Z-level to analyze (default: 0)
        min_size: Minimum room size in cells (default: 4)
        exclude_boundary_touching: Exclude rooms touching grid boundaries
        bounds: Grid boundaries (max_x, max_y). If None, auto-detect.
    
    Returns:
        List of rooms, where each room is a frozenset of cells
    
    Example:
        >>> grid = GridState(_cells={
        ...     (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
        ...     (0,1,0): "wall",                  (2,1,0): "wall",
        ...     (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
        ... })
        >>> rooms = detect_rooms(grid, z_level=0)
        >>> len(rooms)
        1
        >>> (1, 1, 0) in rooms[0]
        True
    
    Complexity:
        O(area) where area = max_x * max_y
    
    Notes:
        - Pure function (no side effects)
        - Deterministic (same grid → same rooms)
        - Z-level independent (each level analyzed separately)
    """
    # Auto-detect bounds if not provided
    if bounds is None:
        bounds = _auto_detect_bounds(grid, z_level)
    
    max_x, max_y = bounds
    
    # Get all occupied cells on this z-level
    occupied = {
        (x, y)
        for x, y, z in grid.all_cells()
        if z == z_level
    }
    
    # Find all empty cells
    all_cells = {(x, y) for x in range(max_x) for y in range(max_y)}
    empty_cells = all_cells - occupied
    
    # Flood-fill to find connected regions
    visited: Set[tuple[int, int]] = set()
    rooms: List[FrozenSet[Cell]] = []
    
    for cell in empty_cells:
        if cell in visited:
            continue
        
        # Flood-fill from this cell
        region = _flood_fill(cell, empty_cells, visited)
        
        # Check size constraint
        if len(region) < min_size:
            continue
        
        # Check boundary constraint
        if exclude_boundary_touching:
            if _touches_boundary(region, max_x, max_y):
                continue
        
        # Convert to 3D cells and add to rooms
        room_3d = frozenset({(x, y, z_level) for x, y in region})
        rooms.append(room_3d)
    
    return rooms


def _flood_fill(
    start: tuple[int, int],
    empty_cells: Set[tuple[int, int]],
    visited: Set[tuple[int, int]]
) -> Set[tuple[int, int]]:
    """
    Flood-fill algorithm to find connected region.
    
    Args:
        start: Starting cell (x, y)
        empty_cells: Set of all empty cells
        visited: Set of already visited cells (modified in-place)
    
    Returns:
        Set of cells in the connected region
    """
    region: Set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque([start])
    visited.add(start)
    
    while queue:
        x, y = queue.popleft()
        region.add((x, y))
        
        # Check 4-connected neighbors
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        for nx, ny in neighbors:
            if (nx, ny) in empty_cells and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    
    return region


def _touches_boundary(
    region: Set[tuple[int, int]],
    max_x: int,
    max_y: int
) -> bool:
    """
    Check if a region touches the grid boundary.
    
    Args:
        region: Set of cells (x, y)
        max_x: Maximum x coordinate (exclusive)
        max_y: Maximum y coordinate (exclusive)
    
    Returns:
        True if region touches boundary
    """
    for x, y in region:
        if x == 0 or x == max_x - 1 or y == 0 or y == max_y - 1:
            return True
    return False


def _auto_detect_bounds(grid: GridState, z_level: int) -> tuple[int, int]:
    """
    Auto-detect grid bounds from occupied cells.
    
    Args:
        grid: Current grid state
        z_level: Z-level to analyze
    
    Returns:
        (max_x, max_y) bounds
    """
    cells_on_level = [
        (x, y)
        for x, y, z in grid.all_cells()
        if z == z_level
    ]
    
    if not cells_on_level:
        return (10, 10)  # Default bounds
    
    max_x = max(x for x, y in cells_on_level) + 2
    max_y = max(y for x, y in cells_on_level) + 2
    
    return (max_x, max_y)


def get_room_stats(rooms: List[FrozenSet[Cell]]) -> dict:
    """
    Get statistics about detected rooms.
    
    Args:
        rooms: List of rooms
    
    Returns:
        Dict with statistics
    
    Example:
        >>> rooms = [frozenset({(1,1,0), (1,2,0)}), frozenset({(5,5,0)})]
        >>> stats = get_room_stats(rooms)
        >>> stats["room_count"]
        2
        >>> stats["total_cells"]
        3
    """
    if not rooms:
        return {
            "room_count": 0,
            "total_cells": 0,
            "avg_room_size": 0.0,
            "min_room_size": 0,
            "max_room_size": 0,
        }
    
    sizes = [len(room) for room in rooms]
    
    return {
        "room_count": len(rooms),
        "total_cells": sum(sizes),
        "avg_room_size": sum(sizes) / len(sizes),
        "min_room_size": min(sizes),
        "max_room_size": max(sizes),
    }


def find_room_at_cell(
    cell: Cell,
    rooms: List[FrozenSet[Cell]]
) -> FrozenSet[Cell] | None:
    """
    Find which room contains a specific cell.
    
    Args:
        cell: Cell to search for
        rooms: List of rooms
    
    Returns:
        Room containing the cell, or None if not found
    
    Example:
        >>> rooms = [frozenset({(1,1,0), (1,2,0)})]
        >>> room = find_room_at_cell((1,1,0), rooms)
        >>> (1,1,0) in room
        True
    """
    for room in rooms:
        if cell in room:
            return room
    return None
