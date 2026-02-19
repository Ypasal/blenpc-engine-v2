"""
grid_state.py - Immutable Structural Grid State

Design Principles:
- Immutable (frozen dataclass)
- Minimal (no behavior, only data)
- Hashable (deterministic state hash)
- No validation logic (handled by validation_engine)
- No collision logic (handled by collision_engine)
- No placement logic (handled by placement_engine)

This is the "truth" of the scene.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet

# Type aliases for clarity
Cell = Tuple[int, int, int]  # (x, y, z) in grid units
ObjectId = str


@dataclass(frozen=True)
class GridState:
    """
    Immutable structural grid state.
    
    Stores only occupancy information:
    - Which cells are occupied
    - Which object occupies each cell
    
    Does NOT store:
    - Object metadata
    - Mesh data
    - Visual properties
    - Collision rules
    - Validation rules
    
    Example:
        >>> grid = GridState.empty()
        >>> grid.is_occupied((0, 0, 0))
        False
        >>> grid.get_object((0, 0, 0))
        None
    """
    
    _cells: Dict[Cell, ObjectId]
    
    # ------------------------
    # Basic Queries
    # ------------------------
    
    def is_occupied(self, cell: Cell) -> bool:
        """Check if a cell is occupied."""
        return cell in self._cells
    
    def get_object(self, cell: Cell) -> ObjectId | None:
        """Get the object ID occupying a cell, or None if empty."""
        return self._cells.get(cell)
    
    def all_cells(self) -> FrozenSet[Cell]:
        """Get all occupied cells as a frozenset."""
        return frozenset(self._cells.keys())
    
    def object_ids(self) -> FrozenSet[ObjectId]:
        """Get all unique object IDs in the grid."""
        return frozenset(self._cells.values())
    
    def size(self) -> int:
        """Get the number of occupied cells."""
        return len(self._cells)
    
    # ------------------------
    # Deterministic Hash
    # ------------------------
    
    def stable_hash(self) -> int:
        """
        Compute a stable, deterministic hash of the grid state.
        
        Order-independent: same cells → same hash, regardless of insertion order.
        
        Returns:
            int: Deterministic hash value
        """
        items = tuple(sorted(self._cells.items()))
        return hash(items)
    
    # ------------------------
    # Factory Methods
    # ------------------------
    
    @staticmethod
    def empty() -> "GridState":
        """Create an empty grid state."""
        return GridState(_cells={})
    
    # ------------------------
    # Python Magic Methods
    # ------------------------
    
    def __len__(self) -> int:
        """Support len(grid) syntax."""
        return len(self._cells)
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"GridState(cells={len(self._cells)}, objects={len(self.object_ids())})"
