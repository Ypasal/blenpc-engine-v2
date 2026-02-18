"""
Test suite for room detection and automation system.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from blenpc.engine.room_detector import auto_complete_room, RoomData
from blenpc.atoms.wall_modular import build_wall
from blenpc.engine.grid_pos import GridPos

def test_auto_complete_room():
    """Test automatic room creation from walls."""
    # Create 4 walls for a 5x5m room
    w1 = build_wall(5.0, 3.0, name="wall_n")
    w1.grid_pos = GridPos(0, 200, 0) # North
    
    w2 = build_wall(5.0, 3.0, name="wall_s")
    w2.grid_pos = GridPos(0, 0, 0)   # South
    
    # Wall thickness is 0.2m (8 units) by default
    # For a 5x5m room, East wall should be at x=200
    w3 = build_wall(0.2, 3.0, name="wall_e")
    w3.grid_pos = GridPos(200, 0, 0) # East
    
    w4 = build_wall(0.2, 3.0, name="wall_w")
    w4.grid_pos = GridPos(0, 0, 0)   # West
    
    room = auto_complete_room([w1, w2, w3, w4])
    
    assert room.name == "auto_room"
    assert len(room.walls) == 4
    # Area calculation:
    # x: 0 to 200+8 = 208 units (5.2m)
    # y: 0 to 200+8 = 208 units (5.2m)
    # Area = 5.2 * 5.2 = 27.04 m2
    assert room.area_m2 == pytest.approx(27.04, abs=0.1)
    assert room.has_floor is True
    assert room.has_ceiling is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
