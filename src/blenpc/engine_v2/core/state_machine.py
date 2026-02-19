"""
state_machine.py - Lightweight State Machine

Design Principles:
- Minimal orchestrator
- Mutable wrapper around immutable GridState
- Optional history tracking
- Simple API

This is NOT a heavy state machine framework.
It's a convenience wrapper for common operations.
"""

from typing import FrozenSet, Optional
from .grid_state import GridState, Cell, ObjectId
from .placement_engine import place_object, remove_object, move_object
from .state_diff import StateHistory


class Engine:
    """
    Lightweight engine wrapper with mutable state.
    
    Wraps immutable GridState with a mutable interface for convenience.
    Optionally tracks state history for undo/redo.
    
    Example:
        >>> engine = Engine()
        >>> engine.place("wall_01", frozenset({(0,0,0)}))
        >>> engine.state.is_occupied((0,0,0))
        True
        >>> engine.undo()
        >>> engine.state.is_occupied((0,0,0))
        False
    
    Notes:
        - This is a convenience wrapper
        - For advanced use cases, use core functions directly
        - State is still immutable internally
    """
    
    def __init__(
        self,
        initial_state: Optional[GridState] = None,
        enable_history: bool = True
    ):
        """
        Initialize engine.
        
        Args:
            initial_state: Starting grid state (default: empty)
            enable_history: Enable undo/redo history
        """
        self._state = initial_state or GridState.empty()
        self._enable_history = enable_history
        
        if enable_history:
            self._history = StateHistory()
            self._history.push(self._state)
        else:
            self._history = None
    
    @property
    def state(self) -> GridState:
        """Get current grid state (read-only)."""
        return self._state
    
    def place(
        self,
        object_id: ObjectId,
        footprint: FrozenSet[Cell],
        bounds: tuple[int, int, int] | None = None
    ) -> GridState:
        """
        Place an object on the grid.
        
        Args:
            object_id: Unique identifier
            footprint: Cells to occupy
            bounds: Optional boundary limits
        
        Returns:
            New grid state
        
        Raises:
            ValueError: If placement fails
        """
        new_state = place_object(object_id, footprint, self._state, bounds)
        self._update_state(new_state)
        return new_state
    
    def remove(self, object_id: ObjectId) -> GridState:
        """
        Remove an object from the grid.
        
        Args:
            object_id: ID of object to remove
        
        Returns:
            New grid state
        
        Raises:
            ValueError: If object not found
        """
        new_state = remove_object(object_id, self._state)
        self._update_state(new_state)
        return new_state
    
    def move(
        self,
        object_id: ObjectId,
        new_footprint: FrozenSet[Cell],
        bounds: tuple[int, int, int] | None = None
    ) -> GridState:
        """
        Move an object to a new position.
        
        Args:
            object_id: ID of object to move
            new_footprint: New footprint
            bounds: Optional boundary limits
        
        Returns:
            New grid state
        
        Raises:
            ValueError: If move fails
        """
        new_state = move_object(object_id, new_footprint, self._state, bounds)
        self._update_state(new_state)
        return new_state
    
    def reset(self) -> None:
        """Reset to empty grid."""
        self._update_state(GridState.empty())
    
    def load_state(self, state: GridState) -> None:
        """
        Load a specific grid state.
        
        Args:
            state: Grid state to load
        """
        self._update_state(state)
    
    def _update_state(self, new_state: GridState) -> None:
        """Internal: Update state and history."""
        self._state = new_state
        
        if self._enable_history and self._history:
            self._history.push(new_state)
    
    # Undo/Redo Operations
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self._history is not None and self._history.can_undo()
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self._history is not None and self._history.can_redo()
    
    def undo(self) -> GridState:
        """
        Undo to previous state.
        
        Returns:
            Previous grid state
        
        Raises:
            ValueError: If undo not possible or history disabled
        """
        if not self._history:
            raise ValueError("History is disabled")
        
        self._state = self._history.undo()
        return self._state
    
    def redo(self) -> GridState:
        """
        Redo to next state.
        
        Returns:
            Next grid state
        
        Raises:
            ValueError: If redo not possible or history disabled
        """
        if not self._history:
            raise ValueError("History is disabled")
        
        self._state = self._history.redo()
        return self._state
    
    def clear_history(self) -> None:
        """Clear undo/redo history."""
        if self._history:
            self._history.clear()
            self._history.push(self._state)
    
    # Query Operations
    
    def is_occupied(self, cell: Cell) -> bool:
        """Check if a cell is occupied."""
        return self._state.is_occupied(cell)
    
    def get_object(self, cell: Cell) -> ObjectId | None:
        """Get object ID at a cell."""
        return self._state.get_object(cell)
    
    def get_stats(self) -> dict:
        """
        Get engine statistics.
        
        Returns:
            Dict with statistics
        """
        stats = {
            "occupied_cells": len(self._state),
            "unique_objects": len(self._state.object_ids()),
            "state_hash": self._state.stable_hash(),
        }
        
        if self._history:
            stats["history_size"] = self._history.size()
            stats["can_undo"] = self._history.can_undo()
            stats["can_redo"] = self._history.can_redo()
        
        return stats
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"Engine("
            f"cells={len(self._state)}, "
            f"objects={len(self._state.object_ids())}, "
            f"history={'enabled' if self._history else 'disabled'})"
        )
