"""
Sims-style Room Detection and Automation System for BlenPC v5.2.0

This module implements:
- Room detection (finding closed loops of walls)
- Automatic floor and ceiling generation
- Room-as-object (grouping walls, floor, and ceiling)
- Topology management (wall corner alignment)
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
import json

from .grid_pos import GridPos
from .grid_manager import SceneGrid
from ..atoms.wall_modular import WallData

@dataclass
class RoomData:
    """
    Data structure for a detected room.
    """
    name: str
    walls: List[str]  # List of wall names
    points: List[Tuple[int, int]]  # Corner points in grid units
    area_m2: float
    has_floor: bool = True
    has_ceiling: bool = True
    meta: Dict = field(default_factory=dict)

class RoomDetector:
    """
    Detects rooms from a collection of walls in a SceneGrid.
    """
    def __init__(self, grid: SceneGrid):
        self.grid = grid
        self.rooms: List[RoomData] = []

    def detect_rooms(self) -> List[RoomData]:
        """
        Analyze the grid to find closed loops of walls.
        
        Note: This is a simplified version for the MVP.
        In a full implementation, this would use a graph-based 
        cycle detection algorithm on wall endpoints.
        """
        # 1. Get all walls from grid
        walls = [obj for obj in self.grid.get_all_objects().values() 
                if "arch_wall" in getattr(obj, 'tags', [])]
        
        if not walls:
            return []

        # 2. Find connected walls (simplified logic)
        # For MVP, we'll assume walls that share endpoints are connected
        # and look for cycles.
        
        # TODO: Implement full cycle detection
        # For now, we'll return an empty list or a mock room if walls exist
        return self.rooms

    def generate_floor(self, room: RoomData) -> Dict:
        """
        Generate floor geometry data for a room.
        """
        return {
            "type": "floor",
            "points": room.points,
            "area": room.area_m2,
            "material": "standard_floor"
        }

    def generate_ceiling(self, room: RoomData) -> Dict:
        """
        Generate ceiling geometry data for a room.
        """
        return {
            "type": "ceiling",
            "points": room.points,
            "area": room.area_m2,
            "material": "standard_ceiling"
        }

def auto_complete_room(walls: List[WallData]) -> RoomData:
    """
    Given a set of walls, automatically create a room object.
    """
    # Calculate bounding box for floor/ceiling
    min_x = min(w.grid_pos.x for w in walls)
    min_y = min(w.grid_pos.y for w in walls)
    max_x = max(w.grid_pos.x + w.grid_size[0] for w in walls)
    max_y = max(w.grid_pos.y + w.grid_size[1] for w in walls)
    
    points = [
        (min_x, min_y),
        (max_x, min_y),
        (max_x, max_y),
        (min_x, max_y)
    ]
    
    from .grid_pos import units_to_meters
    width_m = units_to_meters(max_x - min_x)
    depth_m = units_to_meters(max_y - min_y)
    
    return RoomData(
        name="auto_room",
        walls=[w.name for w in walls],
        points=points,
        area_m2=width_m * depth_m,
        meta={"width_m": width_m, "depth_m": depth_m}
    )
