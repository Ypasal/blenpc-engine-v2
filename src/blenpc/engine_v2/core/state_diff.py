"""
state_diff.py - Grid State Diff System

Design Principles:
- Immutable diff objects
- Simple set operations
- Supports undo/redo
- Minimal memory footprint

Use Cases:
- Undo/redo functionality
- State history tracking
- Network synchronization
- Replay systems
"""

from dataclasses import dataclass
from typing import FrozenSet
from .grid_state import GridState, Cell


@dataclass(frozen=True)
class GridDiff:
    """
    Immutable diff between two grid states.
    
    Represents the changes needed to transform one grid state into another.
    
    Attributes:
        added: Cells that were added
        removed: Cells that were removed
    
    Example:
        >>> old = GridState(_cells={(0,0,0): "obj1"})
        >>> new = GridState(_cells={(0,0,0): "obj1", (1,0,0): "obj2"})
        >>> diff = compute_diff(old, new)
        >>> diff.added
        frozenset({(1, 0, 0)})
        >>> diff.removed
        frozenset()
    """
    
    added: FrozenSet[Cell]
    removed: FrozenSet[Cell]
    
    def is_empty(self) -> bool:
        """Check if diff is empty (no changes)."""
        return len(self.added) == 0 and len(self.removed) == 0
    
    def size(self) -> int:
        """Get total number of changed cells."""
        return len(self.added) + len(self.removed)
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"GridDiff(added={len(self.added)}, removed={len(self.removed)})"


def compute_diff(old: GridState, new: GridState) -> GridDiff:
    """
    Compute the diff between two grid states.
    
    Args:
        old: Previous grid state
        new: New grid state
    
    Returns:
        GridDiff representing the changes
    
    Example:
        >>> old = GridState.empty()
        >>> new = GridState(_cells={(0,0,0): "wall"})
        >>> diff = compute_diff(old, new)
        >>> len(diff.added)
        1
        >>> len(diff.removed)
        0
    
    Complexity:
        O(n + m) where n = len(old), m = len(new)
    
    Notes:
        - Pure function (no side effects)
        - Deterministic
        - Symmetric: compute_diff(a, b) is inverse of compute_diff(b, a)
    """
    old_cells = set(old.all_cells())
    new_cells = set(new.all_cells())
    
    return GridDiff(
        added=frozenset(new_cells - old_cells),
        removed=frozenset(old_cells - new_cells),
    )


def apply_diff(grid: GridState, diff: GridDiff) -> GridState:
    """
    Apply a diff to a grid state.
    
    Note: This is a simplified version that only tracks cell presence,
    not object IDs. For full undo/redo, use state history.
    
    Args:
        grid: Current grid state
        diff: Diff to apply
    
    Returns:
        New grid state with diff applied
    
    Warning:
        This function cannot restore object IDs for removed cells.
        Use full state history for complete undo/redo.
    """
    # This is intentionally limited - use state history for full undo/redo
    raise NotImplementedError(
        "apply_diff() is not implemented. "
        "Use StateHistory for proper undo/redo functionality."
    )


def invert_diff(diff: GridDiff) -> GridDiff:
    """
    Invert a diff (swap added and removed).
    
    Args:
        diff: Diff to invert
    
    Returns:
        Inverted diff
    
    Example:
        >>> diff = GridDiff(
        ...     added=frozenset({(0,0,0)}),
        ...     removed=frozenset({(1,0,0)})
        ... )
        >>> inv = invert_diff(diff)
        >>> inv.added
        frozenset({(1, 0, 0)})
        >>> inv.removed
        frozenset({(0, 0, 0)})
    
    Use Case:
        Undo operation: apply inverted diff
    """
    return GridDiff(
        added=diff.removed,
        removed=diff.added,
    )


@dataclass
class StateHistory:
    """
    Simple state history for undo/redo.
    
    Stores full grid states (not diffs) for simplicity.
    For large grids, consider using diff-based history.
    
    Example:
        >>> history = StateHistory()
        >>> grid1 = GridState.empty()
        >>> history.push(grid1)
        >>> grid2 = place_object("wall", footprint, grid1)
        >>> history.push(grid2)
        >>> history.can_undo()
        True
        >>> previous = history.undo()
        >>> previous == grid1
        True
    """
    
    _states: list[GridState]
    _current_index: int
    
    def __init__(self):
        """Initialize empty history."""
        self._states = []
        self._current_index = -1
    
    def push(self, state: GridState) -> None:
        """
        Push a new state onto the history.
        
        Discards any redo states.
        """
        # Discard states after current index (redo history)
        self._states = self._states[:self._current_index + 1]
        
        # Add new state
        self._states.append(state)
        self._current_index += 1
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self._current_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self._current_index < len(self._states) - 1
    
    def undo(self) -> GridState:
        """
        Undo to previous state.
        
        Returns:
            Previous grid state
        
        Raises:
            ValueError: If undo not possible
        """
        if not self.can_undo():
            raise ValueError("Cannot undo: no previous state")
        
        self._current_index -= 1
        return self._states[self._current_index]
    
    def redo(self) -> GridState:
        """
        Redo to next state.
        
        Returns:
            Next grid state
        
        Raises:
            ValueError: If redo not possible
        """
        if not self.can_redo():
            raise ValueError("Cannot redo: no next state")
        
        self._current_index += 1
        return self._states[self._current_index]
    
    def current(self) -> GridState:
        """
        Get current state.
        
        Returns:
            Current grid state
        
        Raises:
            ValueError: If history is empty
        """
        if self._current_index < 0:
            raise ValueError("History is empty")
        
        return self._states[self._current_index]
    
    def clear(self) -> None:
        """Clear all history."""
        self._states = []
        self._current_index = -1
    
    def size(self) -> int:
        """Get number of states in history."""
        return len(self._states)
