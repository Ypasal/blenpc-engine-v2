"""
test_integration.py - Integration Tests

End-to-end scenarios testing the full engine workflow.
"""

import pytest
from ..core import (
    Engine,
    GridState,
    detect_rooms,
    build_structural_graph,
    find_connected_components,
    get_room_stats,
    get_graph_stats
)


class TestBasicWorkflow:
    """Test basic engine workflow."""
    
    def test_place_and_query(self):
        """Place objects and query state."""
        engine = Engine()
        
        # Place objects
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(1, 0, 0)}))
        engine.place("wall_03", frozenset({(5, 5, 0)}))
        
        # Query state
        assert engine.is_occupied((0, 0, 0))
        assert engine.is_occupied((1, 0, 0))
        assert engine.is_occupied((5, 5, 0))
        assert not engine.is_occupied((10, 10, 0))
        
        # Check stats
        stats = engine.get_stats()
        assert stats["occupied_cells"] == 3
        assert stats["unique_objects"] == 3
    
    def test_place_move_remove(self):
        """Place, move, and remove objects."""
        engine = Engine()
        
        # Place
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        assert engine.is_occupied((0, 0, 0))
        
        # Move
        engine.move("wall_01", frozenset({(5, 5, 0)}))
        assert not engine.is_occupied((0, 0, 0))
        assert engine.is_occupied((5, 5, 0))
        
        # Remove
        engine.remove("wall_01")
        assert not engine.is_occupied((5, 5, 0))
        assert len(engine.state) == 0
    
    def test_undo_redo_workflow(self):
        """Undo and redo operations."""
        engine = Engine()
        
        # Place objects
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(1, 0, 0)}))
        
        assert len(engine.state) == 2
        
        # Undo
        engine.undo()
        assert len(engine.state) == 1
        
        engine.undo()
        assert len(engine.state) == 0
        
        # Redo
        engine.redo()
        assert len(engine.state) == 1
        
        engine.redo()
        assert len(engine.state) == 2


class TestRoomDetectionIntegration:
    """Test room detection with engine."""
    
    def test_detect_room_after_placement(self):
        """Detect rooms after placing walls."""
        engine = Engine()
        
        # Create a simple room (3x3 with walls around edges)
        for x in range(5):
            engine.place(f"wall_bottom_{x}", frozenset({(x, 0, 0)}))
            engine.place(f"wall_top_{x}", frozenset({(x, 4, 0)}))
        
        for y in range(1, 4):
            engine.place(f"wall_left_{y}", frozenset({(0, y, 0)}))
            engine.place(f"wall_right_{y}", frozenset({(4, y, 0)}))
        
        # Detect rooms
        rooms = detect_rooms(engine.state, z_level=0, bounds=(5, 5), min_size=1, exclude_boundary_touching=False)
        
        # Should detect at least one room
        assert len(rooms) >= 1
        
        # Center should be in a room
        assert any((2, 2, 0) in room for room in rooms)
    
    def test_room_stats_integration(self):
        """Get room statistics."""
        engine = Engine()
        
        # Create walls (avoid corners to prevent collision)
        for x in range(3):
            engine.place(f"wall_h_{x}", frozenset({(x, 0, 0)}))
            engine.place(f"wall_h2_{x}", frozenset({(x, 2, 0)}))
        
        for y in range(1, 2):  # Only middle row to avoid collision
            engine.place(f"wall_v_{y}", frozenset({(0, y, 0)}))
            engine.place(f"wall_v2_{y}", frozenset({(2, y, 0)}))
        
        # Detect rooms
        rooms = detect_rooms(engine.state, z_level=0, bounds=(3, 3), min_size=1, exclude_boundary_touching=False)
        
        # Get stats
        stats = get_room_stats(rooms)
        
        assert stats["room_count"] >= 1
        assert stats["total_cells"] >= 1


class TestStructuralGraphIntegration:
    """Test structural graph with engine."""
    
    def test_build_graph_after_placement(self):
        """Build graph after placing objects."""
        engine = Engine()
        
        # Place connected objects
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(1, 0, 0)}))
        engine.place("wall_03", frozenset({(2, 0, 0)}))
        
        # Build graph
        graph = build_structural_graph(engine.state)
        
        # Check connections
        assert "wall_02" in graph["wall_01"]
        assert "wall_03" in graph["wall_02"]
        assert "wall_01" not in graph["wall_03"]
    
    def test_connected_components_integration(self):
        """Find connected components."""
        engine = Engine()
        
        # Create two separate groups
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(1, 0, 0)}))
        
        engine.place("wall_03", frozenset({(10, 10, 0)}))
        engine.place("wall_04", frozenset({(11, 10, 0)}))
        
        # Build graph
        graph = build_structural_graph(engine.state)
        
        # Find components
        components = find_connected_components(graph)
        
        # Should have 2 components
        assert len(components) == 2
    
    def test_graph_stats_integration(self):
        """Get graph statistics."""
        engine = Engine()
        
        # Place objects
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        engine.place("wall_02", frozenset({(1, 0, 0)}))
        engine.place("wall_03", frozenset({(5, 5, 0)}))
        
        # Build graph
        graph = build_structural_graph(engine.state)
        
        # Get stats
        stats = get_graph_stats(graph)
        
        assert stats["node_count"] == 3
        assert stats["edge_count"] == 1  # Only wall_01 and wall_02 connected
        assert stats["isolated_count"] == 1  # wall_03 isolated


class TestComplexScenario:
    """Test complex real-world scenarios."""
    
    def test_build_house_scenario(self):
        """Build a simple house and analyze it."""
        engine = Engine()
        
        # Build outer walls (10x10)
        for x in range(10):
            engine.place(f"wall_bottom_{x}", frozenset({(x, 0, 0)}))
            engine.place(f"wall_top_{x}", frozenset({(x, 9, 0)}))
        
        for y in range(1, 9):
            engine.place(f"wall_left_{y}", frozenset({(0, y, 0)}))
            engine.place(f"wall_right_{y}", frozenset({(9, y, 0)}))
        
        # Add internal wall (dividing room)
        for y in range(1, 9):
            if y != 4:  # Leave door at y=4
                engine.place(f"wall_internal_{y}", frozenset({(5, y, 0)}))
        
        # Check state
        stats = engine.get_stats()
        assert stats["occupied_cells"] > 0
        
        # Detect rooms
        rooms = detect_rooms(engine.state, z_level=0, bounds=(10, 10), min_size=4, exclude_boundary_touching=False)
        
        # Should detect at least 1 room
        assert len(rooms) >= 1
        
        # Build graph
        graph = build_structural_graph(engine.state)
        graph_stats = get_graph_stats(graph)
        
        assert graph_stats["node_count"] > 0
        assert graph_stats["edge_count"] > 0
    
    def test_multi_floor_scenario(self):
        """Test multi-floor building."""
        engine = Engine()
        
        # Floor 0
        for x in range(5):
            engine.place(f"floor0_wall_{x}", frozenset({(x, 0, 0)}))
        
        # Floor 1
        for x in range(5):
            engine.place(f"floor1_wall_{x}", frozenset({(x, 0, 1)}))
        
        # Detect rooms on each floor
        rooms_floor0 = detect_rooms(engine.state, z_level=0, bounds=(5, 5))
        rooms_floor1 = detect_rooms(engine.state, z_level=1, bounds=(5, 5))
        
        # Floors are independent
        assert isinstance(rooms_floor0, list)
        assert isinstance(rooms_floor1, list)


class TestDeterminism:
    """Test deterministic behavior across operations."""
    
    def test_same_operations_same_result(self):
        """Same operations produce same result."""
        # Engine 1
        engine1 = Engine(enable_history=False)
        engine1.place("wall_01", frozenset({(0, 0, 0)}))
        engine1.place("wall_02", frozenset({(1, 0, 0)}))
        hash1 = engine1.state.stable_hash()
        
        # Engine 2
        engine2 = Engine(enable_history=False)
        engine2.place("wall_01", frozenset({(0, 0, 0)}))
        engine2.place("wall_02", frozenset({(1, 0, 0)}))
        hash2 = engine2.state.stable_hash()
        
        assert hash1 == hash2
    
    def test_undo_redo_determinism(self):
        """Undo/redo maintains determinism."""
        engine = Engine()
        
        engine.place("wall_01", frozenset({(0, 0, 0)}))
        original_hash = engine.state.stable_hash()
        
        engine.place("wall_02", frozenset({(5, 5, 0)}))
        engine.undo()
        
        final_hash = engine.state.stable_hash()
        
        assert original_hash == final_hash


class TestPerformance:
    """Basic performance sanity checks."""
    
    def test_large_grid_placement(self):
        """Place many objects."""
        engine = Engine(enable_history=False)
        
        # Place 100 objects
        for i in range(100):
            x = i % 10
            y = i // 10
            engine.place(f"wall_{i}", frozenset({(x, y, 0)}))
        
        assert len(engine.state) == 100
    
    def test_room_detection_performance(self):
        """Room detection on moderate grid."""
        engine = Engine(enable_history=False)
        
        # Create a 20x20 grid with some walls
        for x in range(20):
            engine.place(f"wall_bottom_{x}", frozenset({(x, 0, 0)}))
            engine.place(f"wall_top_{x}", frozenset({(x, 19, 0)}))
        
        for y in range(1, 19):
            engine.place(f"wall_left_{y}", frozenset({(0, y, 0)}))
            engine.place(f"wall_right_{y}", frozenset({(19, y, 0)}))
        
        # Detect rooms (should complete quickly)
        rooms = detect_rooms(engine.state, z_level=0, bounds=(20, 20))
        
        assert isinstance(rooms, list)
