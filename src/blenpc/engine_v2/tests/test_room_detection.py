"""
test_room_detection.py - Tests for Room Detection
"""

import pytest
from ..core.grid_state import GridState
from ..core.room_detection import (
    detect_rooms,
    get_room_stats,
    find_room_at_cell
)


class TestRoomDetectionBasics:
    """Test basic room detection."""
    
    def test_empty_grid_no_rooms(self):
        """Empty grid should have no rooms."""
        grid = GridState.empty()
        rooms = detect_rooms(grid, bounds=(10, 10))
        
        assert len(rooms) == 0
    
    def test_single_enclosed_room(self):
        """Single enclosed room."""
        # Create a 3x3 grid with walls around the edges
        cells = {}
        for x in range(5):
            cells[(x, 0, 0)] = "wall"  # Bottom wall
            cells[(x, 4, 0)] = "wall"  # Top wall
        for y in range(5):
            cells[(0, y, 0)] = "wall"  # Left wall
            cells[(4, y, 0)] = "wall"  # Right wall
        
        grid = GridState(_cells=cells)
        rooms = detect_rooms(grid, bounds=(5, 5), exclude_boundary_touching=False)
        
        assert len(rooms) >= 1
        # Center area should be a room
        assert any((2, 2, 0) in room for room in rooms)
    
    def test_multiple_rooms(self):
        """Multiple separate rooms."""
        # Two separate enclosed areas
        cells = {
            # Room 1 walls
            (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
            (0,1,0): "wall",                  (2,1,0): "wall",
            (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
            
            # Room 2 walls
            (5,0,0): "wall", (6,0,0): "wall", (7,0,0): "wall",
            (5,1,0): "wall",                  (7,1,0): "wall",
            (5,2,0): "wall", (6,2,0): "wall", (7,2,0): "wall",
        }
        grid = GridState(_cells=cells)
        rooms = detect_rooms(grid, bounds=(10, 10), min_size=1, exclude_boundary_touching=False)
        
        # Should detect at least 2 rooms
        assert len(rooms) >= 2


class TestRoomDetectionMinSize:
    """Test minimum size filtering."""
    
    def test_min_size_filter(self):
        """Rooms smaller than min_size are filtered out."""
        # Create a small 1-cell "room"
        cells = {
            (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
            (0,1,0): "wall",                  (2,1,0): "wall",
            (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
        }
        grid = GridState(_cells=cells)
        
        # With min_size=1, should detect room
        rooms_1 = detect_rooms(grid, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        assert len(rooms_1) >= 1
        
        # With min_size=10, should not detect room (too small)
        rooms_10 = detect_rooms(grid, bounds=(3, 3), min_size=10, exclude_boundary_touching=False)
        assert len(rooms_10) == 0


class TestRoomDetectionBoundary:
    """Test boundary touching exclusion."""
    
    def test_exclude_boundary_touching(self):
        """Rooms touching boundary are excluded."""
        # Create a room that touches the boundary
        cells = {
            (1,0,0): "wall", (2,0,0): "wall",
            (1,1,0): "wall", (2,1,0): "wall",
        }
        grid = GridState(_cells=cells)
        
        # With exclude_boundary_touching=True, no rooms
        rooms_excluded = detect_rooms(grid, bounds=(5, 5), min_size=1, exclude_boundary_touching=True)
        assert len(rooms_excluded) == 0
        
        # With exclude_boundary_touching=False, should find room
        rooms_included = detect_rooms(grid, bounds=(5, 5), min_size=1, exclude_boundary_touching=False)
        assert len(rooms_included) >= 1


class TestRoomDetectionZLevel:
    """Test z-level separation."""
    
    def test_different_z_levels(self):
        """Rooms on different z-levels are separate."""
        cells = {
            # Level 0
            (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
            (0,1,0): "wall",                  (2,1,0): "wall",
            (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
            
            # Level 1 (same pattern)
            (0,0,1): "wall", (1,0,1): "wall", (2,0,1): "wall",
            (0,1,1): "wall",                  (2,1,1): "wall",
            (0,2,1): "wall", (1,2,1): "wall", (2,2,1): "wall",
        }
        grid = GridState(_cells=cells)
        
        rooms_z0 = detect_rooms(grid, z_level=0, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        rooms_z1 = detect_rooms(grid, z_level=1, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        
        # Both levels should have rooms
        assert len(rooms_z0) >= 1
        assert len(rooms_z1) >= 1
        
        # Rooms should be on correct z-level
        for room in rooms_z0:
            for x, y, z in room:
                assert z == 0
        
        for room in rooms_z1:
            for x, y, z in room:
                assert z == 1


class TestRoomStats:
    """Test room statistics."""
    
    def test_stats_empty(self):
        """Stats for empty room list."""
        stats = get_room_stats([])
        
        assert stats["room_count"] == 0
        assert stats["total_cells"] == 0
    
    def test_stats_single_room(self):
        """Stats for single room."""
        rooms = [frozenset({(1,1,0), (1,2,0), (2,1,0)})]
        stats = get_room_stats(rooms)
        
        assert stats["room_count"] == 1
        assert stats["total_cells"] == 3
        assert stats["min_room_size"] == 3
        assert stats["max_room_size"] == 3
    
    def test_stats_multiple_rooms(self):
        """Stats for multiple rooms."""
        rooms = [
            frozenset({(1,1,0), (1,2,0)}),  # Size 2
            frozenset({(5,5,0), (5,6,0), (6,5,0)}),  # Size 3
        ]
        stats = get_room_stats(rooms)
        
        assert stats["room_count"] == 2
        assert stats["total_cells"] == 5
        assert stats["min_room_size"] == 2
        assert stats["max_room_size"] == 3
        assert stats["avg_room_size"] == 2.5


class TestFindRoomAtCell:
    """Test finding room at specific cell."""
    
    def test_find_room_existing(self):
        """Find room containing a cell."""
        rooms = [
            frozenset({(1,1,0), (1,2,0)}),
            frozenset({(5,5,0), (5,6,0)}),
        ]
        
        room = find_room_at_cell((1,1,0), rooms)
        
        assert room is not None
        assert (1,1,0) in room
        assert (1,2,0) in room
    
    def test_find_room_nonexistent(self):
        """Find room for cell not in any room."""
        rooms = [
            frozenset({(1,1,0), (1,2,0)}),
        ]
        
        room = find_room_at_cell((10,10,0), rooms)
        
        assert room is None


class TestRoomDetectionDeterminism:
    """Test deterministic behavior."""
    
    def test_deterministic_detection(self):
        """Same grid should produce same rooms."""
        cells = {
            (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
            (0,1,0): "wall",                  (2,1,0): "wall",
            (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
        }
        grid = GridState(_cells=cells)
        
        rooms1 = detect_rooms(grid, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        rooms2 = detect_rooms(grid, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        
        assert len(rooms1) == len(rooms2)


class TestRoomDetectionEdgeCases:
    """Test edge cases."""
    
    def test_fully_occupied_grid(self):
        """Fully occupied grid has no rooms."""
        cells = {(x, y, 0): "wall" for x in range(5) for y in range(5)}
        grid = GridState(_cells=cells)
        
        rooms = detect_rooms(grid, bounds=(5, 5))
        
        assert len(rooms) == 0
    
    def test_single_cell_room(self):
        """Single cell room (if min_size allows)."""
        cells = {
            (0,0,0): "wall", (1,0,0): "wall", (2,0,0): "wall",
            (0,1,0): "wall",                  (2,1,0): "wall",
            (0,2,0): "wall", (1,2,0): "wall", (2,2,0): "wall",
        }
        grid = GridState(_cells=cells)
        
        rooms = detect_rooms(grid, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        
        assert len(rooms) >= 1
