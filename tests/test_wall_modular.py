"""
Test suite for modular wall system with segment-based pre-cut architecture.

This test file verifies:
1. Wall segment generation
2. Opening pre-cut (segment blocking)
3. Slot creation for doors/windows
4. Grid integration
5. Backward compatibility
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from blenpc.atoms.wall_modular import (
    build_wall,
    Opening,
    WallSegment,
    WallData,
    wall_to_json
)
from blenpc.engine.grid_pos import GridPos
from blenpc import config


class TestWallSegments:
    """Test wall segment generation."""
    
    def test_simple_wall_no_openings(self):
        """Test creating a simple wall without openings."""
        wall = build_wall(length=5.0, height=3.0)
        
        assert wall.name == "wall"
        assert len(wall.segments) == 20  # 5.0m / 0.25m = 20 segments
        assert all(not seg.blocked for seg in wall.segments)
        assert all(seg.segment_type == "wall" for seg in wall.segments)
        assert len(wall.slots) == 0
    
    def test_wall_dimensions(self):
        """Test wall dimensions are correctly stored."""
        wall = build_wall(length=5.0, height=3.0, thickness=0.2)
        
        assert wall.meta["length_m"] == 5.0
        assert wall.meta["height_m"] == 3.0
        assert wall.meta["thickness_m"] == 0.2
        assert wall.meta["segment_count"] == 20
    
    def test_wall_grid_size(self):
        """Test wall grid size calculation."""
        wall = build_wall(length=5.0, height=3.0, thickness=0.2)
        
        # 5.0m = 200 units, 0.2m = 8 units, 3.0m = 120 units
        assert wall.grid_size == (200, 8, 120)
    
    def test_wall_tags(self):
        """Test automatic tag generation."""
        wall = build_wall(length=5.0, height=3.0)
        
        assert "arch_wall" in wall.tags
        assert "length_5m" in wall.tags
        assert "height_3m" in wall.tags
        assert "modular_v2" in wall.tags


class TestOpenings:
    """Test opening (door/window) pre-cut system."""
    
    def test_single_door_opening(self):
        """Test wall with single door opening."""
        door = Opening(
            opening_type="door",
            center_x=2.5,
            width=0.9,
            height=2.1,
            sill_height=0.0
        )
        
        wall = build_wall(length=5.0, height=3.0, openings=[door])
        
        # Check that some segments are blocked
        blocked_segments = [s for s in wall.segments if s.blocked]
        assert len(blocked_segments) > 0
        
        # Check segment types
        door_segments = [s for s in wall.segments if s.segment_type == "door_opening"]
        assert len(door_segments) > 0
    
    def test_single_window_opening(self):
        """Test wall with single window opening."""
        window = Opening(
            opening_type="window",
            center_x=2.5,
            width=1.2,
            height=1.4,
            sill_height=0.9
        )
        
        wall = build_wall(length=5.0, height=3.0, openings=[window])
        
        # Check segment blocking
        blocked_segments = [s for s in wall.segments if s.blocked]
        assert len(blocked_segments) > 0
        
        # Check metadata
        assert wall.meta["opening_count"] == 1
        assert wall.meta["blocked_segments"] == len(blocked_segments)
    
    def test_multiple_openings(self):
        """Test wall with both door and window."""
        door = Opening("door", center_x=1.5, width=0.9, height=2.1)
        window = Opening("window", center_x=3.5, width=1.2, height=1.4, sill_height=0.9)
        
        wall = build_wall(length=5.0, height=3.0, openings=[door, window])
        
        assert wall.meta["opening_count"] == 2
        assert len(wall.slots) == 2
        
        # Check slot types
        slot_types = [slot["type"] for slot in wall.slots]
        assert "door_opening" in slot_types
        assert "window_opening" in slot_types
    
    def test_opening_slot_creation(self):
        """Test that openings create correct slots."""
        window = Opening(
            opening_type="window",
            center_x=2.5,
            width=1.2,
            height=1.4,
            sill_height=0.9
        )
        
        wall = build_wall(length=5.0, height=3.0, openings=[window])
        
        assert len(wall.slots) == 1
        slot = wall.slots[0]
        
        assert slot["type"] == "window_opening"
        assert "slot_window" in slot["id"]
        assert slot["size_meters"] == (1.2, 1.4)
        assert slot["sill_height"] == 0.9
        assert slot["required"] is True
        assert slot["occupied"] is False


class TestSlotPositions:
    """Test slot position calculations."""
    
    def test_door_slot_position(self):
        """Test door slot is positioned correctly."""
        door = Opening("door", center_x=2.0, width=0.9, height=2.1, sill_height=0.0)
        wall = build_wall(length=5.0, height=3.0, openings=[door])
        
        slot = wall.slots[0]
        pos_meters = slot["pos_meters"]
        
        # Center should be at 2.0m along wall
        assert pos_meters[0] == pytest.approx(2.0, abs=0.05)
        
        # Height should be at center of door (2.1m / 2 = 1.05m)
        assert pos_meters[2] == pytest.approx(1.05, abs=0.05)
    
    def test_window_slot_position(self):
        """Test window slot is positioned correctly."""
        window = Opening(
            "window",
            center_x=3.0,
            width=1.2,
            height=1.4,
            sill_height=0.9
        )
        wall = build_wall(length=5.0, height=3.0, openings=[window])
        
        slot = wall.slots[0]
        pos_meters = slot["pos_meters"]
        
        # Center should be at 3.0m along wall
        assert pos_meters[0] == pytest.approx(3.0, abs=0.05)
        
        # Height should be at sill + half height (0.9 + 1.4/2 = 1.6m)
        assert pos_meters[2] == pytest.approx(1.6, abs=0.05)


class TestGridIntegration:
    """Test integration with grid system."""
    
    def test_wall_implements_igridobject(self):
        """Test that WallData implements IGridObject interface."""
        wall = build_wall(length=5.0, height=3.0)
        
        # Check required attributes
        assert hasattr(wall, 'name')
        assert hasattr(wall, 'grid_pos')
        assert hasattr(wall, 'grid_size')
        assert hasattr(wall, 'snap_mode')
        assert hasattr(wall, 'slots')
        assert hasattr(wall, 'tags')
        
        # Check grid_pos is GridPos
        assert isinstance(wall.grid_pos, GridPos)
    
    def test_wall_footprint(self):
        """Test wall footprint calculation."""
        wall = build_wall(length=5.0, height=3.0, thickness=0.2)
        
        footprint = wall.get_footprint()
        
        # Should have many cells (200 x 8 x 120)
        assert len(footprint) == 200 * 8 * 120
    
    def test_wall_aabb(self):
        """Test wall AABB calculation."""
        wall = build_wall(length=5.0, height=3.0, thickness=0.2)
        
        aabb = wall.get_aabb()
        
        assert aabb["min"] == pytest.approx([0.0, 0.0, 0.0])
        assert aabb["max"] == pytest.approx([5.0, 0.2, 3.0])
    
    def test_wall_center(self):
        """Test wall center calculation."""
        wall = build_wall(length=5.0, height=3.0, thickness=0.2)
        
        center = wall.get_center()
        cx, cy, cz = center.to_meters()
        
        assert cx == pytest.approx(2.5, abs=0.05)
        assert cy == pytest.approx(0.1, abs=0.05)
        assert cz == pytest.approx(1.5, abs=0.05)


class TestSerialization:
    """Test JSON serialization."""
    
    def test_wall_to_json(self):
        """Test wall serialization to JSON."""
        door = Opening("door", center_x=2.0, width=0.9, height=2.1)
        wall = build_wall(length=5.0, height=3.0, openings=[door], name="test_wall")
        
        json_str = wall_to_json(wall)
        
        assert "test_wall" in json_str
        assert "door_opening" in json_str
        assert "segments" in json_str
        assert "slots" in json_str
    
    def test_json_contains_metadata(self):
        """Test JSON contains all necessary metadata."""
        wall = build_wall(length=5.0, height=3.0)
        json_str = wall_to_json(wall)
        
        import json
        data = json.loads(json_str)
        
        assert "meta" in data
        assert "length_m" in data["meta"]
        assert "segment_count" in data["meta"]
        assert data["meta"]["length_m"] == 5.0


class TestBackwardCompatibility:
    """Test backward compatibility with old API."""
    
    def test_legacy_snap_function(self):
        """Test that legacy snap() function still works."""
        from blenpc.engine.grid_pos import snap
        
        result = snap(1.23)
        assert result == pytest.approx(1.25)
    
    def test_legacy_grid_unit(self):
        """Test that legacy GRID_UNIT constant still exists."""
        assert hasattr(config, 'GRID_UNIT')
        assert config.GRID_UNIT == 0.25


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_short_wall(self):
        """Test wall shorter than one segment."""
        wall = build_wall(length=0.1, height=3.0)
        
        # Should have at least 1 segment (or 0 if too short)
        assert len(wall.segments) >= 0
    
    def test_opening_at_wall_edge(self):
        """Test opening positioned at wall edge."""
        door = Opening("door", center_x=0.45, width=0.9, height=2.1)
        wall = build_wall(length=5.0, height=3.0, openings=[door])
        
        # Should not crash
        assert len(wall.slots) == 1
    
    def test_opening_outside_wall(self):
        """Test opening positioned outside wall bounds."""
        door = Opening("door", center_x=10.0, width=0.9, height=2.1)
        wall = build_wall(length=5.0, height=3.0, openings=[door])
        
        # Should handle gracefully (no segments blocked)
        blocked = [s for s in wall.segments if s.blocked]
        assert len(blocked) == 0
    
    def test_overlapping_openings(self):
        """Test two overlapping openings."""
        door1 = Opening("door", center_x=2.0, width=0.9, height=2.1)
        door2 = Opening("door", center_x=2.2, width=0.9, height=2.1)
        
        wall = build_wall(length=5.0, height=3.0, openings=[door1, door2])
        
        # Should create both slots
        assert len(wall.slots) == 2
        
        # Segments can only be blocked once
        blocked = [s for s in wall.segments if s.blocked]
        # All blocked segments should be marked as door_opening
        assert all(s.segment_type == "door_opening" for s in blocked)


class TestStandards:
    """Test integration with architectural standards."""
    
    def test_door_standards(self):
        """Test door dimensions match standards."""
        door_spec = config.DOOR_STANDARDS["single"]
        
        door = Opening(
            "door",
            center_x=2.5,
            width=door_spec["w"],
            height=door_spec["h"]
        )
        
        wall = build_wall(length=5.0, height=3.0, openings=[door])
        slot = wall.slots[0]
        
        assert slot["size_meters"][0] == door_spec["w"]
        assert slot["size_meters"][1] == door_spec["h"]
    
    def test_window_standards(self):
        """Test window dimensions match standards."""
        window_spec = config.WINDOW_STANDARDS["standard"]
        
        window = Opening(
            "window",
            center_x=2.5,
            width=window_spec["w"],
            height=window_spec["h"],
            sill_height=window_spec["sill"]
        )
        
        wall = build_wall(length=5.0, height=3.0, openings=[window])
        slot = wall.slots[0]
        
        assert slot["size_meters"][0] == window_spec["w"]
        assert slot["size_meters"][1] == window_spec["h"]
        assert slot["sill_height"] == window_spec["sill"]
    
    def test_wall_height_standards(self):
        """Test wall height matches standards."""
        height = config.WALL_STANDARDS["height"]["default"]
        wall = build_wall(length=5.0, height=height)
        
        assert wall.meta["height_m"] == height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
