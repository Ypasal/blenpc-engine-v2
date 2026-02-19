"""
test_grid_state.py - Tests for GridState

TDD approach: tests written first, then implementation verified.
"""

import pytest
from ..core.grid_state import GridState, Cell, ObjectId


class TestGridStateBasics:
    """Test basic GridState functionality."""
    
    def test_empty_grid_creation(self):
        """Empty grid should have no cells."""
        grid = GridState.empty()
        assert len(grid) == 0
        assert grid.size() == 0
        assert len(grid.all_cells()) == 0
        assert len(grid.object_ids()) == 0
    
    def test_grid_is_frozen(self):
        """GridState dataclass should be frozen."""
        grid = GridState.empty()
        # Frozen dataclass prevents attribute reassignment
        with pytest.raises(Exception):  # FrozenInstanceError
            grid._cells = {}
    
    def test_is_occupied_empty_grid(self):
        """Empty grid should report all cells as unoccupied."""
        grid = GridState.empty()
        assert not grid.is_occupied((0, 0, 0))
        assert not grid.is_occupied((100, 200, 300))
    
    def test_get_object_empty_grid(self):
        """Empty grid should return None for all cells."""
        grid = GridState.empty()
        assert grid.get_object((0, 0, 0)) is None
        assert grid.get_object((100, 200, 300)) is None


class TestGridStateWithData:
    """Test GridState with actual data."""
    
    def test_grid_with_single_cell(self):
        """Grid with one occupied cell."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        
        assert len(grid) == 1
        assert grid.is_occupied((0, 0, 0))
        assert grid.get_object((0, 0, 0)) == "wall_01"
        assert not grid.is_occupied((1, 0, 0))
    
    def test_grid_with_multiple_cells(self):
        """Grid with multiple occupied cells."""
        cells = {
            (0, 0, 0): "wall_01",
            (1, 0, 0): "wall_01",
            (2, 0, 0): "wall_02",
        }
        grid = GridState(_cells=cells)
        
        assert len(grid) == 3
        assert grid.is_occupied((0, 0, 0))
        assert grid.is_occupied((1, 0, 0))
        assert grid.is_occupied((2, 0, 0))
        assert grid.get_object((0, 0, 0)) == "wall_01"
        assert grid.get_object((2, 0, 0)) == "wall_02"
    
    def test_all_cells_returns_frozenset(self):
        """all_cells() should return a frozenset."""
        cells = {
            (0, 0, 0): "obj1",
            (1, 0, 0): "obj2",
        }
        grid = GridState(_cells=cells)
        
        all_cells = grid.all_cells()
        assert isinstance(all_cells, frozenset)
        assert (0, 0, 0) in all_cells
        assert (1, 0, 0) in all_cells
        assert len(all_cells) == 2
    
    def test_object_ids_returns_unique(self):
        """object_ids() should return unique object IDs."""
        cells = {
            (0, 0, 0): "wall_01",
            (1, 0, 0): "wall_01",  # Same object
            (2, 0, 0): "wall_02",
        }
        grid = GridState(_cells=cells)
        
        obj_ids = grid.object_ids()
        assert isinstance(obj_ids, frozenset)
        assert len(obj_ids) == 2  # Only 2 unique IDs
        assert "wall_01" in obj_ids
        assert "wall_02" in obj_ids


class TestGridStateDeterminism:
    """Test deterministic behavior of GridState."""
    
    def test_stable_hash_empty_grid(self):
        """Empty grids should have same hash."""
        grid1 = GridState.empty()
        grid2 = GridState.empty()
        assert grid1.stable_hash() == grid2.stable_hash()
    
    def test_stable_hash_same_content(self):
        """Grids with same content should have same hash."""
        cells1 = {(0, 0, 0): "obj1", (1, 0, 0): "obj2"}
        cells2 = {(0, 0, 0): "obj1", (1, 0, 0): "obj2"}
        
        grid1 = GridState(_cells=cells1)
        grid2 = GridState(_cells=cells2)
        
        assert grid1.stable_hash() == grid2.stable_hash()
    
    def test_stable_hash_order_independent(self):
        """Hash should be same regardless of insertion order."""
        # Python dicts maintain insertion order (3.7+), but hash should ignore it
        cells1 = {(0, 0, 0): "obj1", (1, 0, 0): "obj2"}
        cells2 = {(1, 0, 0): "obj2", (0, 0, 0): "obj1"}
        
        grid1 = GridState(_cells=cells1)
        grid2 = GridState(_cells=cells2)
        
        assert grid1.stable_hash() == grid2.stable_hash()
    
    def test_stable_hash_different_content(self):
        """Grids with different content should have different hash."""
        grid1 = GridState(_cells={(0, 0, 0): "obj1"})
        grid2 = GridState(_cells={(1, 0, 0): "obj2"})
        
        assert grid1.stable_hash() != grid2.stable_hash()


class TestGridStateRepr:
    """Test string representation."""
    
    def test_repr_empty(self):
        """Empty grid repr."""
        grid = GridState.empty()
        repr_str = repr(grid)
        assert "GridState" in repr_str
        assert "cells=0" in repr_str
    
    def test_repr_with_data(self):
        """Grid with data repr."""
        cells = {
            (0, 0, 0): "wall_01",
            (1, 0, 0): "wall_01",
            (2, 0, 0): "wall_02",
        }
        grid = GridState(_cells=cells)
        repr_str = repr(grid)
        assert "GridState" in repr_str
        assert "cells=3" in repr_str
        assert "objects=2" in repr_str


class TestGridState3D:
    """Test 3D grid support."""
    
    def test_3d_cells(self):
        """Grid should support 3D cells."""
        cells = {
            (0, 0, 0): "floor",
            (0, 0, 1): "wall",
            (0, 0, 2): "ceiling",
        }
        grid = GridState(_cells=cells)
        
        assert grid.is_occupied((0, 0, 0))
        assert grid.is_occupied((0, 0, 1))
        assert grid.is_occupied((0, 0, 2))
        assert not grid.is_occupied((0, 0, 3))
    
    def test_2d_as_special_case(self):
        """2D grids are just 3D with z=0."""
        cells = {
            (0, 0, 0): "obj1",
            (1, 0, 0): "obj2",
        }
        grid = GridState(_cells=cells)
        
        assert grid.is_occupied((0, 0, 0))
        assert grid.is_occupied((1, 0, 0))
        assert not grid.is_occupied((0, 0, 1))  # Different z-level
