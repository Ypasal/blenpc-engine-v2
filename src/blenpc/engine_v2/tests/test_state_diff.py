"""
test_state_diff.py - Tests for State Diff System
"""

import pytest
from ..core.grid_state import GridState
from ..core.state_diff import GridDiff, compute_diff, invert_diff, StateHistory
from ..core.placement_engine import place_object


class TestGridDiff:
    """Test GridDiff dataclass."""
    
    def test_empty_diff(self):
        """Empty diff has no changes."""
        diff = GridDiff(added=frozenset(), removed=frozenset())
        
        assert diff.is_empty()
        assert diff.size() == 0
    
    def test_diff_with_added(self):
        """Diff with only added cells."""
        diff = GridDiff(
            added=frozenset({(0,0,0), (1,0,0)}),
            removed=frozenset()
        )
        
        assert not diff.is_empty()
        assert diff.size() == 2
        assert len(diff.added) == 2
        assert len(diff.removed) == 0
    
    def test_diff_with_removed(self):
        """Diff with only removed cells."""
        diff = GridDiff(
            added=frozenset(),
            removed=frozenset({(0,0,0)})
        )
        
        assert not diff.is_empty()
        assert diff.size() == 1
    
    def test_diff_with_both(self):
        """Diff with both added and removed."""
        diff = GridDiff(
            added=frozenset({(0,0,0)}),
            removed=frozenset({(5,0,0)})
        )
        
        assert diff.size() == 2


class TestComputeDiff:
    """Test diff computation."""
    
    def test_diff_empty_to_empty(self):
        """Diff between two empty grids."""
        old = GridState.empty()
        new = GridState.empty()
        
        diff = compute_diff(old, new)
        
        assert diff.is_empty()
    
    def test_diff_empty_to_occupied(self):
        """Diff from empty to occupied grid."""
        old = GridState.empty()
        new = GridState(_cells={(0,0,0): "wall"})
        
        diff = compute_diff(old, new)
        
        assert len(diff.added) == 1
        assert (0,0,0) in diff.added
        assert len(diff.removed) == 0
    
    def test_diff_occupied_to_empty(self):
        """Diff from occupied to empty grid."""
        old = GridState(_cells={(0,0,0): "wall"})
        new = GridState.empty()
        
        diff = compute_diff(old, new)
        
        assert len(diff.added) == 0
        assert len(diff.removed) == 1
        assert (0,0,0) in diff.removed
    
    def test_diff_add_and_remove(self):
        """Diff with both additions and removals."""
        old = GridState(_cells={(0,0,0): "wall1"})
        new = GridState(_cells={(5,0,0): "wall2"})
        
        diff = compute_diff(old, new)
        
        assert len(diff.added) == 1
        assert (5,0,0) in diff.added
        assert len(diff.removed) == 1
        assert (0,0,0) in diff.removed
    
    def test_diff_same_grid(self):
        """Diff between identical grids."""
        grid = GridState(_cells={(0,0,0): "wall", (1,0,0): "wall"})
        
        diff = compute_diff(grid, grid)
        
        assert diff.is_empty()
    
    def test_diff_deterministic(self):
        """Diff computation is deterministic."""
        old = GridState.empty()
        new = GridState(_cells={(0,0,0): "wall"})
        
        diff1 = compute_diff(old, new)
        diff2 = compute_diff(old, new)
        
        assert diff1.added == diff2.added
        assert diff1.removed == diff2.removed


class TestInvertDiff:
    """Test diff inversion."""
    
    def test_invert_empty_diff(self):
        """Inverting empty diff gives empty diff."""
        diff = GridDiff(added=frozenset(), removed=frozenset())
        inv = invert_diff(diff)
        
        assert inv.is_empty()
    
    def test_invert_added_becomes_removed(self):
        """Inverting swaps added and removed."""
        diff = GridDiff(
            added=frozenset({(0,0,0)}),
            removed=frozenset({(5,0,0)})
        )
        inv = invert_diff(diff)
        
        assert inv.added == diff.removed
        assert inv.removed == diff.added
    
    def test_double_invert_is_identity(self):
        """Inverting twice gives original."""
        diff = GridDiff(
            added=frozenset({(0,0,0)}),
            removed=frozenset({(5,0,0)})
        )
        
        double_inv = invert_diff(invert_diff(diff))
        
        assert double_inv.added == diff.added
        assert double_inv.removed == diff.removed


class TestStateHistory:
    """Test state history for undo/redo."""
    
    def test_empty_history(self):
        """Empty history."""
        history = StateHistory()
        
        assert not history.can_undo()
        assert not history.can_redo()
        assert history.size() == 0
    
    def test_push_single_state(self):
        """Push single state."""
        history = StateHistory()
        grid = GridState.empty()
        
        history.push(grid)
        
        assert history.size() == 1
        assert not history.can_undo()
        assert not history.can_redo()
    
    def test_push_multiple_states(self):
        """Push multiple states."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        
        assert history.size() == 2
        assert history.can_undo()
        assert not history.can_redo()
    
    def test_undo_single_step(self):
        """Undo single step."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        
        previous = history.undo()
        
        assert previous == grid1
        assert history.can_redo()
    
    def test_redo_single_step(self):
        """Redo single step."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        history.undo()
        
        next_state = history.redo()
        
        assert next_state == grid2
        assert not history.can_redo()
    
    def test_undo_redo_cycle(self):
        """Undo then redo returns to same state."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        
        history.undo()
        final = history.redo()
        
        assert final == grid2
    
    def test_push_after_undo_discards_redo(self):
        """Pushing after undo discards redo history."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        grid3 = GridState(_cells={(5,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        history.undo()
        history.push(grid3)  # Discards grid2
        
        assert not history.can_redo()
        assert history.size() == 2
    
    def test_undo_raises_when_not_possible(self):
        """Undo raises error when not possible."""
        history = StateHistory()
        grid = GridState.empty()
        history.push(grid)
        
        with pytest.raises(ValueError, match="Cannot undo"):
            history.undo()
    
    def test_redo_raises_when_not_possible(self):
        """Redo raises error when not possible."""
        history = StateHistory()
        grid = GridState.empty()
        history.push(grid)
        
        with pytest.raises(ValueError, match="Cannot redo"):
            history.redo()
    
    def test_current_state(self):
        """Get current state."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        
        assert history.current() == grid2
    
    def test_current_after_undo(self):
        """Current state after undo."""
        history = StateHistory()
        grid1 = GridState.empty()
        grid2 = GridState(_cells={(0,0,0): "wall"})
        
        history.push(grid1)
        history.push(grid2)
        history.undo()
        
        assert history.current() == grid1
    
    def test_clear_history(self):
        """Clear all history."""
        history = StateHistory()
        history.push(GridState.empty())
        history.push(GridState(_cells={(0,0,0): "wall"}))
        
        history.clear()
        
        assert history.size() == 0
        assert not history.can_undo()
        assert not history.can_redo()


class TestStateHistoryIntegration:
    """Test state history with actual placements."""
    
    def test_history_with_placements(self):
        """History tracks placements correctly."""
        history = StateHistory()
        
        grid0 = GridState.empty()
        history.push(grid0)
        
        grid1 = place_object("wall_01", frozenset({(0,0,0)}), grid0)
        history.push(grid1)
        
        grid2 = place_object("wall_02", frozenset({(5,0,0)}), grid1)
        history.push(grid2)
        
        # Undo twice
        history.undo()
        history.undo()
        
        assert history.current() == grid0
        assert len(history.current()) == 0
    
    def test_history_undo_redo_sequence(self):
        """Complex undo/redo sequence."""
        history = StateHistory()
        
        grid0 = GridState.empty()
        history.push(grid0)
        
        grid1 = place_object("wall_01", frozenset({(0,0,0)}), grid0)
        history.push(grid1)
        
        grid2 = place_object("wall_02", frozenset({(5,0,0)}), grid1)
        history.push(grid2)
        
        # Undo, redo, undo
        history.undo()
        assert history.current() == grid1
        
        history.redo()
        assert history.current() == grid2
        
        history.undo()
        assert history.current() == grid1
