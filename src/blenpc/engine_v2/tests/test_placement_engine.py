"""
test_placement_engine.py - Tests for Placement Engine
"""

import pytest
from ..core.grid_state import GridState
from ..core.placement_engine import (
    place_object,
    remove_object,
    move_object,
    place_multiple
)


class TestPlaceObject:
    """Test object placement."""
    
    def test_place_single_cell(self):
        """Place object with single cell footprint."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0)})
        
        new_grid = place_object("wall_01", footprint, grid)
        
        assert new_grid.is_occupied((0, 0, 0))
        assert new_grid.get_object((0, 0, 0)) == "wall_01"
        assert len(new_grid) == 1
    
    def test_place_multiple_cells(self):
        """Place object with multiple cells."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0), (1, 0, 0), (2, 0, 0)})
        
        new_grid = place_object("wall_01", footprint, grid)
        
        assert len(new_grid) == 3
        assert all(new_grid.get_object(cell) == "wall_01" for cell in footprint)
    
    def test_place_preserves_original_grid(self):
        """Placement should not modify original grid."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0)})
        
        new_grid = place_object("wall_01", footprint, grid)
        
        assert len(grid) == 0  # Original unchanged
        assert len(new_grid) == 1  # New grid has object
    
    def test_place_collision_raises_error(self):
        """Placement on occupied cell should raise error."""
        grid = GridState(_cells={(0, 0, 0): "existing"})
        footprint = frozenset({(0, 0, 0), (1, 0, 0)})
        
        with pytest.raises(ValueError, match="Collision detected"):
            place_object("new_obj", footprint, grid)
    
    def test_place_empty_id_raises_error(self):
        """Empty object ID should raise error."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0)})
        
        with pytest.raises(ValueError, match="object_id cannot be empty"):
            place_object("", footprint, grid)
    
    def test_place_empty_footprint_raises_error(self):
        """Empty footprint should raise error."""
        grid = GridState.empty()
        footprint = frozenset()
        
        with pytest.raises(ValueError, match="footprint cannot be empty"):
            place_object("wall_01", footprint, grid)
    
    def test_place_with_bounds(self):
        """Placement within bounds should succeed."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0), (1, 0, 0)})
        bounds = (10, 10, 10)
        
        new_grid = place_object("wall_01", footprint, grid, bounds)
        
        assert len(new_grid) == 2
    
    def test_place_out_of_bounds_raises_error(self):
        """Placement outside bounds should raise error."""
        grid = GridState.empty()
        footprint = frozenset({(15, 0, 0)})  # Outside bounds
        bounds = (10, 10, 10)
        
        with pytest.raises(ValueError, match="out of bounds"):
            place_object("wall_01", footprint, grid, bounds)


class TestRemoveObject:
    """Test object removal."""
    
    def test_remove_single_cell_object(self):
        """Remove object with single cell."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        
        new_grid = remove_object("wall_01", grid)
        
        assert len(new_grid) == 0
        assert not new_grid.is_occupied((0, 0, 0))
    
    def test_remove_multi_cell_object(self):
        """Remove object with multiple cells."""
        grid = GridState(_cells={
            (0, 0, 0): "wall_01",
            (1, 0, 0): "wall_01",
            (2, 0, 0): "wall_01",
        })
        
        new_grid = remove_object("wall_01", grid)
        
        assert len(new_grid) == 0
    
    def test_remove_preserves_other_objects(self):
        """Removing one object should not affect others."""
        grid = GridState(_cells={
            (0, 0, 0): "wall_01",
            (5, 0, 0): "wall_02",
        })
        
        new_grid = remove_object("wall_01", grid)
        
        assert len(new_grid) == 1
        assert new_grid.is_occupied((5, 0, 0))
        assert new_grid.get_object((5, 0, 0)) == "wall_02"
    
    def test_remove_nonexistent_raises_error(self):
        """Removing nonexistent object should raise error."""
        grid = GridState.empty()
        
        with pytest.raises(ValueError, match="not found"):
            remove_object("nonexistent", grid)
    
    def test_remove_preserves_original_grid(self):
        """Removal should not modify original grid."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        
        new_grid = remove_object("wall_01", grid)
        
        assert len(grid) == 1  # Original unchanged
        assert len(new_grid) == 0  # New grid empty


class TestMoveObject:
    """Test object movement."""
    
    def test_move_to_empty_location(self):
        """Move object to empty location."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        new_footprint = frozenset({(5, 0, 0)})
        
        new_grid = move_object("wall_01", new_footprint, grid)
        
        assert not new_grid.is_occupied((0, 0, 0))  # Old location empty
        assert new_grid.is_occupied((5, 0, 0))  # New location occupied
        assert new_grid.get_object((5, 0, 0)) == "wall_01"
    
    def test_move_changes_footprint_size(self):
        """Move can change footprint size."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        new_footprint = frozenset({(5, 0, 0), (6, 0, 0), (7, 0, 0)})
        
        new_grid = move_object("wall_01", new_footprint, grid)
        
        assert len(new_grid) == 3
    
    def test_move_to_occupied_location_raises_error(self):
        """Moving to occupied location should raise error."""
        grid = GridState(_cells={
            (0, 0, 0): "wall_01",
            (5, 0, 0): "wall_02",
        })
        new_footprint = frozenset({(5, 0, 0)})
        
        with pytest.raises(ValueError, match="Collision detected"):
            move_object("wall_01", new_footprint, grid)
    
    def test_move_nonexistent_raises_error(self):
        """Moving nonexistent object should raise error."""
        grid = GridState.empty()
        new_footprint = frozenset({(5, 0, 0)})
        
        with pytest.raises(ValueError, match="not found"):
            move_object("nonexistent", new_footprint, grid)


class TestPlaceMultiple:
    """Test multiple object placement."""
    
    def test_place_multiple_objects(self):
        """Place multiple objects in sequence."""
        grid = GridState.empty()
        placements = [
            ("wall_01", frozenset({(0, 0, 0)})),
            ("wall_02", frozenset({(5, 0, 0)})),
            ("wall_03", frozenset({(10, 0, 0)})),
        ]
        
        new_grid = place_multiple(placements, grid)
        
        assert len(new_grid) == 3
        assert len(new_grid.object_ids()) == 3
    
    def test_place_multiple_deterministic(self):
        """Multiple placements should be deterministic."""
        grid = GridState.empty()
        placements = [
            ("wall_01", frozenset({(0, 0, 0)})),
            ("wall_02", frozenset({(5, 0, 0)})),
        ]
        
        grid1 = place_multiple(placements, grid)
        grid2 = place_multiple(placements, grid)
        
        assert grid1.stable_hash() == grid2.stable_hash()
    
    def test_place_multiple_fails_on_collision(self):
        """Multiple placements should fail if any collides."""
        grid = GridState.empty()
        placements = [
            ("wall_01", frozenset({(0, 0, 0)})),
            ("wall_02", frozenset({(0, 0, 0)})),  # Collision!
        ]
        
        with pytest.raises(ValueError, match="Collision detected"):
            place_multiple(placements, grid)
    
    def test_place_multiple_empty_list(self):
        """Empty placement list should return unchanged grid."""
        grid = GridState.empty()
        placements = []
        
        new_grid = place_multiple(placements, grid)
        
        assert len(new_grid) == 0
        assert new_grid.stable_hash() == grid.stable_hash()


class TestPlacementDeterminism:
    """Test deterministic behavior of placement."""
    
    def test_same_placement_same_hash(self):
        """Same placement should produce same hash."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0), (1, 0, 0)})
        
        grid1 = place_object("wall_01", footprint, grid)
        grid2 = place_object("wall_01", footprint, grid)
        
        assert grid1.stable_hash() == grid2.stable_hash()
    
    def test_placement_order_matters(self):
        """Different placement order may produce different grid."""
        grid = GridState.empty()
        
        # Order 1
        grid1 = place_object("wall_01", frozenset({(0, 0, 0)}), grid)
        grid1 = place_object("wall_02", frozenset({(5, 0, 0)}), grid1)
        
        # Order 2
        grid2 = place_object("wall_02", frozenset({(5, 0, 0)}), grid)
        grid2 = place_object("wall_01", frozenset({(0, 0, 0)}), grid2)
        
        # Hash should be same (order-independent hash)
        assert grid1.stable_hash() == grid2.stable_hash()
