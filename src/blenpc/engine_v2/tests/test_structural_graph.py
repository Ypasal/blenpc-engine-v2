"""
test_structural_graph.py - Tests for Structural Graph
"""

import pytest
from ..core.grid_state import GridState
from ..core.structural_graph import (
    build_structural_graph,
    find_connected_components,
    get_graph_stats,
    find_neighbors,
    is_connected,
    get_object_degree
)


class TestBuildStructuralGraph:
    """Test graph building."""
    
    def test_empty_grid(self):
        """Empty grid produces empty graph."""
        grid = GridState.empty()
        graph = build_structural_graph(grid)
        
        assert len(graph) == 0
    
    def test_single_object(self):
        """Single object has no connections."""
        grid = GridState(_cells={(0,0,0): "wall_01"})
        graph = build_structural_graph(grid)
        
        assert "wall_01" in graph
        assert len(graph["wall_01"]) == 0
    
    def test_two_adjacent_objects(self):
        """Two adjacent objects are connected."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (1,0,0): "wall_02",  # Adjacent
        })
        graph = build_structural_graph(grid)
        
        assert "wall_02" in graph["wall_01"]
        assert "wall_01" in graph["wall_02"]
    
    def test_two_separate_objects(self):
        """Two separate objects are not connected."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (5,0,0): "wall_02",  # Not adjacent
        })
        graph = build_structural_graph(grid)
        
        assert "wall_02" not in graph["wall_01"]
        assert "wall_01" not in graph["wall_02"]
    
    def test_same_object_multiple_cells(self):
        """Same object occupying multiple cells."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (1,0,0): "wall_01",  # Same object
            (2,0,0): "wall_02",  # Adjacent to wall_01
        })
        graph = build_structural_graph(grid)
        
        assert "wall_02" in graph["wall_01"]
        assert "wall_01" in graph["wall_02"]
    
    def test_three_objects_chain(self):
        """Three objects in a chain."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (1,0,0): "wall_02",
            (2,0,0): "wall_03",
        })
        graph = build_structural_graph(grid)
        
        # wall_01 connects to wall_02
        assert "wall_02" in graph["wall_01"]
        assert "wall_03" not in graph["wall_01"]
        
        # wall_02 connects to both
        assert "wall_01" in graph["wall_02"]
        assert "wall_03" in graph["wall_02"]
        
        # wall_03 connects to wall_02
        assert "wall_02" in graph["wall_03"]
        assert "wall_01" not in graph["wall_03"]


class TestConnectedComponents:
    """Test connected component detection."""
    
    def test_single_component(self):
        """All objects in one component."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01", "wall_03"},
            "wall_03": {"wall_02"},
        }
        components = find_connected_components(graph)
        
        assert len(components) == 1
        assert len(components[0]) == 3
    
    def test_two_components(self):
        """Two separate components."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01"},
            "wall_03": {"wall_04"},
            "wall_04": {"wall_03"},
        }
        components = find_connected_components(graph)
        
        assert len(components) == 2
    
    def test_isolated_nodes(self):
        """Isolated nodes form single-node components."""
        graph = {
            "wall_01": set(),
            "wall_02": set(),
        }
        components = find_connected_components(graph)
        
        assert len(components) == 2
        assert all(len(comp) == 1 for comp in components)


class TestGraphStats:
    """Test graph statistics."""
    
    def test_stats_empty_graph(self):
        """Stats for empty graph."""
        graph = {}
        stats = get_graph_stats(graph)
        
        assert stats["node_count"] == 0
        assert stats["edge_count"] == 0
    
    def test_stats_single_node(self):
        """Stats for single isolated node."""
        graph = {"wall_01": set()}
        stats = get_graph_stats(graph)
        
        assert stats["node_count"] == 1
        assert stats["edge_count"] == 0
        assert stats["isolated_count"] == 1
    
    def test_stats_two_connected_nodes(self):
        """Stats for two connected nodes."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01"},
        }
        stats = get_graph_stats(graph)
        
        assert stats["node_count"] == 2
        assert stats["edge_count"] == 1
        assert stats["isolated_count"] == 0
    
    def test_stats_complex_graph(self):
        """Stats for complex graph."""
        graph = {
            "wall_01": {"wall_02", "wall_03"},
            "wall_02": {"wall_01"},
            "wall_03": {"wall_01"},
            "wall_04": set(),  # Isolated
        }
        stats = get_graph_stats(graph)
        
        assert stats["node_count"] == 4
        assert stats["edge_count"] == 2
        assert stats["isolated_count"] == 1
        assert stats["max_degree"] == 2


class TestFindNeighbors:
    """Test neighbor finding."""
    
    def test_find_neighbors_existing(self):
        """Find neighbors of existing node."""
        graph = {
            "wall_01": {"wall_02", "wall_03"},
            "wall_02": {"wall_01"},
            "wall_03": {"wall_01"},
        }
        neighbors = find_neighbors("wall_01", graph)
        
        assert len(neighbors) == 2
        assert "wall_02" in neighbors
        assert "wall_03" in neighbors
    
    def test_find_neighbors_nonexistent(self):
        """Find neighbors of nonexistent node."""
        graph = {"wall_01": {"wall_02"}}
        neighbors = find_neighbors("nonexistent", graph)
        
        assert len(neighbors) == 0
    
    def test_find_neighbors_isolated(self):
        """Find neighbors of isolated node."""
        graph = {"wall_01": set()}
        neighbors = find_neighbors("wall_01", graph)
        
        assert len(neighbors) == 0


class TestIsConnected:
    """Test connectivity checking."""
    
    def test_directly_connected(self):
        """Two directly connected objects."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01"},
        }
        
        assert is_connected("wall_01", "wall_02", graph)
        assert is_connected("wall_02", "wall_01", graph)
    
    def test_indirectly_connected(self):
        """Two indirectly connected objects."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01", "wall_03"},
            "wall_03": {"wall_02"},
        }
        
        assert is_connected("wall_01", "wall_03", graph)
        assert is_connected("wall_03", "wall_01", graph)
    
    def test_not_connected(self):
        """Two disconnected objects."""
        graph = {
            "wall_01": {"wall_02"},
            "wall_02": {"wall_01"},
            "wall_03": set(),
        }
        
        assert not is_connected("wall_01", "wall_03", graph)
    
    def test_same_object(self):
        """Object is connected to itself."""
        graph = {"wall_01": set()}
        
        assert is_connected("wall_01", "wall_01", graph)
    
    def test_nonexistent_object(self):
        """Nonexistent object is not connected."""
        graph = {"wall_01": set()}
        
        assert not is_connected("wall_01", "nonexistent", graph)


class TestGetObjectDegree:
    """Test degree calculation."""
    
    def test_degree_isolated(self):
        """Isolated object has degree 0."""
        graph = {"wall_01": set()}
        degree = get_object_degree("wall_01", graph)
        
        assert degree == 0
    
    def test_degree_single_connection(self):
        """Object with one connection has degree 1."""
        graph = {"wall_01": {"wall_02"}}
        degree = get_object_degree("wall_01", graph)
        
        assert degree == 1
    
    def test_degree_multiple_connections(self):
        """Object with multiple connections."""
        graph = {"wall_01": {"wall_02", "wall_03", "wall_04"}}
        degree = get_object_degree("wall_01", graph)
        
        assert degree == 3
    
    def test_degree_nonexistent(self):
        """Nonexistent object has degree 0."""
        graph = {"wall_01": set()}
        degree = get_object_degree("nonexistent", graph)
        
        assert degree == 0


class TestGraphDeterminism:
    """Test deterministic behavior."""
    
    def test_deterministic_graph_building(self):
        """Same grid produces same graph."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (1,0,0): "wall_02",
            (2,0,0): "wall_03",
        })
        
        graph1 = build_structural_graph(grid)
        graph2 = build_structural_graph(grid)
        
        assert graph1.keys() == graph2.keys()
        for key in graph1:
            assert graph1[key] == graph2[key]


class TestGraphZLevel:
    """Test z-level handling."""
    
    def test_different_z_levels_not_connected(self):
        """Objects on different z-levels are not connected."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (0,0,1): "wall_02",  # Same x,y but different z
        })
        graph = build_structural_graph(grid)
        
        assert "wall_02" not in graph["wall_01"]
        assert "wall_01" not in graph["wall_02"]
    
    def test_same_z_level_connected(self):
        """Objects on same z-level can be connected."""
        grid = GridState(_cells={
            (0,0,0): "wall_01",
            (1,0,0): "wall_02",
        })
        graph = build_structural_graph(grid)
        
        assert "wall_02" in graph["wall_01"]
