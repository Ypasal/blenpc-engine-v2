"""
test_collision_engine.py - Tests for Collision Engine
"""

import pytest
from ..core.grid_state import GridState, Cell
from ..core.collision_engine import detect_collision, check_overlap


class TestDetectCollision:
    """Test collision detection with grid."""
    
    def test_no_collision_empty_grid(self):
        """Empty grid should never have collision."""
        grid = GridState.empty()
        footprint = frozenset({(0, 0, 0), (1, 0, 0)})
        
        assert not detect_collision(footprint, grid)
    
    def test_collision_single_cell(self):
        """Collision when footprint overlaps one cell."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        footprint = frozenset({(0, 0, 0), (1, 0, 0)})
        
        assert detect_collision(footprint, grid)
    
    def test_no_collision_adjacent_cells(self):
        """Adjacent cells should not collide."""
        grid = GridState(_cells={(0, 0, 0): "wall_01"})
        footprint = frozenset({(1, 0, 0), (2, 0, 0)})
        
        assert not detect_collision(footprint, grid)
    
    def test_collision_multiple_cells(self):
        """Collision when multiple cells overlap."""
        grid = GridState(_cells={
            (0, 0, 0): "wall_01",
            (1, 0, 0): "wall_01",
            (2, 0, 0): "wall_01",
        })
        footprint = frozenset({(1, 0, 0), (2, 0, 0), (3, 0, 0)})
        
        assert detect_collision(footprint, grid)
    
    def test_no_collision_different_z_level(self):
        """Different z-levels should not collide."""
        grid = GridState(_cells={(0, 0, 0): "floor"})
        footprint = frozenset({(0, 0, 1)})  # Same x,y but different z
        
        assert not detect_collision(footprint, grid)
    
    def test_collision_deterministic(self):
        """Same input should always give same result."""
        grid = GridState(_cells={(5, 5, 0): "obj"})
        footprint = frozenset({(5, 5, 0)})
        
        result1 = detect_collision(footprint, grid)
        result2 = detect_collision(footprint, grid)
        result3 = detect_collision(footprint, grid)
        
        assert result1 == result2 == result3 == True


class TestCheckOverlap:
    """Test footprint overlap checking."""
    
    def test_no_overlap_disjoint(self):
        """Disjoint footprints should not overlap."""
        a = frozenset({(0, 0, 0), (1, 0, 0)})
        b = frozenset({(5, 0, 0), (6, 0, 0)})
        
        assert not check_overlap(a, b)
    
    def test_overlap_single_cell(self):
        """Footprints sharing one cell should overlap."""
        a = frozenset({(0, 0, 0), (1, 0, 0)})
        b = frozenset({(1, 0, 0), (2, 0, 0)})
        
        assert check_overlap(a, b)
    
    def test_overlap_multiple_cells(self):
        """Footprints sharing multiple cells should overlap."""
        a = frozenset({(0, 0, 0), (1, 0, 0), (2, 0, 0)})
        b = frozenset({(1, 0, 0), (2, 0, 0), (3, 0, 0)})
        
        assert check_overlap(a, b)
    
    def test_overlap_identical(self):
        """Identical footprints should overlap."""
        a = frozenset({(0, 0, 0), (1, 0, 0)})
        b = frozenset({(0, 0, 0), (1, 0, 0)})
        
        assert check_overlap(a, b)
    
    def test_overlap_symmetric(self):
        """Overlap check should be symmetric."""
        a = frozenset({(0, 0, 0), (1, 0, 0)})
        b = frozenset({(1, 0, 0), (2, 0, 0)})
        
        assert check_overlap(a, b) == check_overlap(b, a)


class TestCollisionPerformance:
    """Test collision detection performance characteristics."""
    
    def test_large_footprint_no_collision(self):
        """Large footprint without collision should be fast."""
        grid = GridState(_cells={(0, 0, 0): "obj"})
        
        # Large footprint far from occupied cell
        footprint = frozenset({(x, 0, 0) for x in range(100, 200)})
        
        assert not detect_collision(footprint, grid)
    
    def test_large_grid_small_footprint(self):
        """Small footprint on large grid should be fast."""
        # Large grid
        cells = {(x, y, 0): f"obj_{x}_{y}" for x in range(50) for y in range(50)}
        grid = GridState(_cells=cells)
        
        # Small footprint in empty area
        footprint = frozenset({(100, 100, 0)})
        
        assert not detect_collision(footprint, grid)


class TestCollisionEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_footprint(self):
        """Empty footprint should never collide."""
        grid = GridState(_cells={(0, 0, 0): "obj"})
        footprint = frozenset()
        
        assert not detect_collision(footprint, grid)
    
    def test_negative_coordinates(self):
        """Negative coordinates should work correctly."""
        grid = GridState(_cells={(-1, -1, 0): "obj"})
        footprint = frozenset({(-1, -1, 0)})
        
        assert detect_collision(footprint, grid)
    
    def test_large_coordinates(self):
        """Large coordinates should work correctly."""
        grid = GridState(_cells={(10000, 10000, 100): "obj"})
        footprint = frozenset({(10000, 10000, 100)})
        
        assert detect_collision(footprint, grid)
