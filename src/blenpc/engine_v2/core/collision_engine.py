"""
collision_engine.py - Pure Collision Detection

Design Principles:
- Pure function (no side effects)
- Stateless (no global state)
- Minimal (set intersection only)
- O(n) complexity where n = footprint size
- No mesh, no bounding box, no SAT, no physics engine

Collision Definition:
    Two footprints collide if they share at least one cell.
    Mathematically: A ∩ B ≠ ∅
"""

from typing import FrozenSet
from .grid_state import GridState, Cell


def detect_collision(
    footprint: FrozenSet[Cell],
    grid: GridState
) -> bool:
    """
    Pure collision detection using set intersection.
    
    Args:
        footprint: Set of cells to check
        grid: Current grid state
    
    Returns:
        True if any cell in footprint is already occupied, False otherwise
    
    Example:
        >>> grid = GridState(_cells={(0,0,0): "wall"})
        >>> footprint = frozenset({(0,0,0), (1,0,0)})
        >>> detect_collision(footprint, grid)
        True
        >>> footprint2 = frozenset({(2,0,0), (3,0,0)})
        >>> detect_collision(footprint2, grid)
        False
    
    Complexity:
        O(n) where n = len(footprint)
        Hash lookup is O(1) per cell
    
    Notes:
        - Does not modify grid
        - Does not raise exceptions
        - Deterministic (same input → same output)
    """
    return not footprint.isdisjoint(grid.all_cells())


def check_overlap(
    footprint_a: FrozenSet[Cell],
    footprint_b: FrozenSet[Cell]
) -> bool:
    """
    Check if two footprints overlap (without grid).
    
    Useful for pre-placement validation.
    
    Args:
        footprint_a: First footprint
        footprint_b: Second footprint
    
    Returns:
        True if footprints share at least one cell
    
    Example:
        >>> a = frozenset({(0,0,0), (1,0,0)})
        >>> b = frozenset({(1,0,0), (2,0,0)})
        >>> check_overlap(a, b)
        True
    """
    return not footprint_a.isdisjoint(footprint_b)
