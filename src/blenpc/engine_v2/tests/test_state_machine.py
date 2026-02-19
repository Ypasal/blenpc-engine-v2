"""
test_state_machine.py - Tests for State Machine (Engine wrapper)
"""

import pytest
from ..core.grid_state import GridState
from ..core.state_machine import Engine


class TestEngineBasics:
    """Test basic engine functionality."""
    
    def test_engine_init_empty(self):
        """Engine initializes with empty grid."""
        engine = Engine()
        
        assert len(engine.state) == 0
        assert not engine.is_occupied((0, 0, 0))
    
    def test_engine_init_with_state(self):
        """Engine can be initialized with existing state."""
        initial = GridState(_cells={(0,0,0): "wall"})
        engine = Engine(initial_state=initial)
        
        assert len(engine.state) == 1
        assert engine.is_occupied((0, 0, 0))
    
    def test_engine_init_history_enabled(self):
        """Engine with history enabled."""
        engine = Engine(enable_history=True)
        
        assert engine.can_undo() is False  # No previous state
        assert engine.can_redo() is False
    
    def test_engine_init_history_disabled(self):
        """Engine with history disabled."""
        engine = Engine(enable_history=False)
        
        with pytest.raises(ValueError, match="History is disabled"):
            engine.undo()


class TestEnginePlacement:
    """Test placement operations."""
    
    def test_place_single_object(self):
        """Place single object."""
        engine = Engine()
        footprint = frozenset({(0, 0, 0)})
        
        engine.place("wall_01", footprint)
        
        assert engine.is_occupied((0, 0, 0))
        assert engine.get_object((0, 0, 0)) == "wall_01"
    
    def test_place_multiple_objects(self):
        """Place multiple objects."""
        engine = Engine()
        
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        
        assert len(engine.state) == 2
    
    def test_place_collision_raises_error(self):
        """Placement collision raises error."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        with pytest.raises(ValueError, match="Collision detected"):
            engine.place("wall_02", frozenset({(0, 0, 0)}))
    
    def test_place_with_bounds(self):
        """Placement with boundary checking."""
        engine = Engine()
        footprint = frozenset({(0, 0, 0)})
        bounds = (10, 10, 10)
        
        engine.place("wall_01", footprint, bounds)
        
        assert engine.is_occupied((0, 0, 0))


class TestEngineRemoval:
    """Test removal operations."""
    
    def test_remove_object(self):
        """Remove object."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        engine.remove("wall_01")
        
        assert not engine.is_occupied((0, 0, 0))
        assert len(engine.state) == 0
    
    def test_remove_nonexistent_raises_error(self):
        """Removing nonexistent object raises error."""
        engine = Engine()
        
        with pytest.raises(ValueError, match="not found"):
            engine.remove("nonexistent")


class TestEngineMovement:
    """Test movement operations."""
    
    def test_move_object(self):
        """Move object to new position."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        engine.move("wall_01", frozenset({(5, 0, 0)}))
        
        assert not engine.is_occupied((0, 0, 0))
        assert engine.is_occupied((5, 0, 0))
        assert engine.get_object((5, 0, 0)) == "wall_01"
    
    def test_move_to_occupied_raises_error(self):
        """Moving to occupied location raises error."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        
        with pytest.raises(ValueError, match="Collision detected"):
            engine.move("wall_01", frozenset({(5, 0, 0)}))


class TestEngineUndoRedo:
    """Test undo/redo functionality."""
    
    def test_undo_single_placement(self):
        """Undo single placement."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        engine.undo()
        
        assert not engine.is_occupied((0, 0, 0))
        assert len(engine.state) == 0
    
    def test_redo_single_placement(self):
        """Redo single placement."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.undo()
        
        engine.redo()
        
        assert engine.is_occupied((0, 0, 0))
    
    def test_undo_redo_cycle(self):
        """Undo then redo returns to same state."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        original_hash = engine.state.stable_hash()
        
        engine.undo()
        engine.redo()
        
        assert engine.state.stable_hash() == original_hash
    
    def test_multiple_undo(self):
        """Multiple undo operations."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        engine.place("wall_03", frozenset({(10, 0, 0)}))
        
        engine.undo()
        assert len(engine.state) == 2
        
        engine.undo()
        assert len(engine.state) == 1
        
        engine.undo()
        assert len(engine.state) == 0
    
    def test_placement_after_undo_discards_redo(self):
        """Placement after undo discards redo history."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        
        engine.undo()
        engine.place("wall_03", frozenset({(10, 0, 0)}))
        
        assert not engine.can_redo()
    
    def test_can_undo_can_redo(self):
        """Check undo/redo availability."""
        engine = Engine()
        
        assert not engine.can_undo()
        assert not engine.can_redo()
        
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        assert engine.can_undo()
        assert not engine.can_redo()
        
        engine.undo()
        
        assert not engine.can_undo()
        assert engine.can_redo()


class TestEngineReset:
    """Test reset functionality."""
    
    def test_reset_to_empty(self):
        """Reset clears all objects."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        
        engine.reset()
        
        assert len(engine.state) == 0
    
    def test_reset_allows_undo(self):
        """Reset can be undone."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        engine.reset()
        engine.undo()
        
        assert len(engine.state) == 1


class TestEngineLoadState:
    """Test state loading."""
    
    def test_load_state(self):
        """Load a specific state."""
        engine = Engine()
        new_state = GridState(_cells={(0,0,0): "wall", (5,0,0): "wall"})
        
        engine.load_state(new_state)
        
        assert len(engine.state) == 2
        assert engine.is_occupied((0, 0, 0))
        assert engine.is_occupied((5, 0, 0))


class TestEngineStats:
    """Test statistics."""
    
    def test_get_stats_empty(self):
        """Stats for empty engine."""
        engine = Engine()
        stats = engine.get_stats()
        
        assert stats["occupied_cells"] == 0
        assert stats["unique_objects"] == 0
        assert "state_hash" in stats
    
    def test_get_stats_with_objects(self):
        """Stats with objects."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0), (1, 0, 0)}))
        
        stats = engine.get_stats()
        
        assert stats["occupied_cells"] == 2
        assert stats["unique_objects"] == 1
    
    def test_get_stats_with_history(self):
        """Stats include history info."""
        engine = Engine(enable_history=True)
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        stats = engine.get_stats()
        
        assert "history_size" in stats
        assert "can_undo" in stats
        assert "can_redo" in stats


class TestEngineClearHistory:
    """Test history clearing."""
    
    def test_clear_history(self):
        """Clear history."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(5, 0, 0)}))
        
        engine.clear_history()
        
        assert not engine.can_undo()
        assert not engine.can_redo()


class TestEngineRepr:
    """Test string representation."""
    
    def test_repr_empty(self):
        """Repr for empty engine."""
        engine = Engine()
        repr_str = repr(engine)
        
        assert "Engine" in repr_str
        assert "cells=0" in repr_str
    
    def test_repr_with_data(self):
        """Repr with data."""
        engine = Engine()
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        
        repr_str = repr(engine)
        
        assert "cells=1" in repr_str
        assert "objects=1" in repr_str
