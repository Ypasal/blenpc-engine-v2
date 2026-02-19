"""
structural_graph.py - Structural Adjacency Graph

Design Principles:
- Pure function (no side effects)
- Read-only (does not modify grid)
- Object-level connectivity (not cell-level)
- O(n) complexity where n = occupied cells
- Undirected graph

Graph Definition:
    Nodes: Object IDs
    Edges: Objects that share adjacent cells (4-connected)

Use Cases:
    - Structural integrity analysis
    - Load propagation
    - Connected component detection
    - Constraint solving
"""

from typing import Dict, Set, List, FrozenSet
from .grid_state import GridState, Cell, ObjectId


def build_structural_graph(grid: GridState) -> Dict[ObjectId, Set[ObjectId]]:
    """
    Build adjacency graph of objects based on cell connectivity.
    
    Args:
        grid: Current grid state
    
    Returns:
        Adjacency dict: object_id -> set of connected object_ids
    
    Example:
        >>> grid = GridState(_cells={
        ...     (0,0,0): "wall_01",
        ...     (1,0,0): "wall_02",  # Adjacent to wall_01
        ...     (5,0,0): "wall_03",  # Not adjacent
        ... })
        >>> graph = build_structural_graph(grid)
        >>> "wall_02" in graph["wall_01"]
        True
        >>> "wall_03" in graph["wall_01"]
        False
    
    Complexity:
        O(n) where n = number of occupied cells
    
    Notes:
        - Pure function (no side effects)
        - Deterministic
        - Undirected graph (if A connects to B, B connects to A)
        - 4-connected (only orthogonal neighbors)
    """
    graph: Dict[ObjectId, Set[ObjectId]] = {}
    
    # Initialize graph with all objects
    for obj_id in grid.object_ids():
        graph[obj_id] = set()
    
    # Build edges based on cell adjacency
    for cell in grid.all_cells():
        obj_id = grid.get_object(cell)
        if not obj_id:
            continue
        
        x, y, z = cell
        
        # Check 4-connected neighbors
        neighbors = [
            (x+1, y, z),
            (x-1, y, z),
            (x, y+1, z),
            (x, y-1, z),
        ]
        
        for neighbor_cell in neighbors:
            neighbor_obj = grid.get_object(neighbor_cell)
            
            # Add edge if neighbor exists and is different object
            if neighbor_obj and neighbor_obj != obj_id:
                graph[obj_id].add(neighbor_obj)
    
    return graph


def find_connected_components(
    graph: Dict[ObjectId, Set[ObjectId]]
) -> List[FrozenSet[ObjectId]]:
    """
    Find connected components in the structural graph.
    
    Args:
        graph: Adjacency graph
    
    Returns:
        List of connected components (each is a frozenset of object IDs)
    
    Example:
        >>> graph = {
        ...     "wall_01": {"wall_02"},
        ...     "wall_02": {"wall_01"},
        ...     "wall_03": set(),  # Isolated
        ... }
        >>> components = find_connected_components(graph)
        >>> len(components)
        2
    
    Use Case:
        Detect isolated structures or groups of connected objects.
    """
    visited: Set[ObjectId] = set()
    components: List[FrozenSet[ObjectId]] = []
    
    for obj_id in graph:
        if obj_id in visited:
            continue
        
        # DFS to find connected component
        component = _dfs_component(obj_id, graph, visited)
        components.append(frozenset(component))
    
    return components


def _dfs_component(
    start: ObjectId,
    graph: Dict[ObjectId, Set[ObjectId]],
    visited: Set[ObjectId]
) -> Set[ObjectId]:
    """
    DFS to find connected component starting from a node.
    
    Args:
        start: Starting object ID
        graph: Adjacency graph
        visited: Set of visited nodes (modified in-place)
    
    Returns:
        Set of object IDs in the connected component
    """
    component: Set[ObjectId] = set()
    stack: List[ObjectId] = [start]
    
    while stack:
        obj_id = stack.pop()
        
        if obj_id in visited:
            continue
        
        visited.add(obj_id)
        component.add(obj_id)
        
        # Add neighbors to stack
        for neighbor in graph.get(obj_id, set()):
            if neighbor not in visited:
                stack.append(neighbor)
    
    return component


def get_graph_stats(graph: Dict[ObjectId, Set[ObjectId]]) -> dict:
    """
    Get statistics about the structural graph.
    
    Args:
        graph: Adjacency graph
    
    Returns:
        Dict with statistics
    
    Example:
        >>> graph = {"wall_01": {"wall_02"}, "wall_02": {"wall_01"}}
        >>> stats = get_graph_stats(graph)
        >>> stats["node_count"]
        2
        >>> stats["edge_count"]
        1
    """
    node_count = len(graph)
    
    # Count edges (undirected, so divide by 2)
    edge_count = sum(len(neighbors) for neighbors in graph.values()) // 2
    
    # Find isolated nodes
    isolated = [obj_id for obj_id, neighbors in graph.items() if not neighbors]
    
    # Degree statistics
    degrees = [len(neighbors) for neighbors in graph.values()]
    avg_degree = sum(degrees) / len(degrees) if degrees else 0.0
    
    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "isolated_count": len(isolated),
        "avg_degree": avg_degree,
        "max_degree": max(degrees) if degrees else 0,
        "min_degree": min(degrees) if degrees else 0,
    }


def find_neighbors(
    object_id: ObjectId,
    graph: Dict[ObjectId, Set[ObjectId]]
) -> Set[ObjectId]:
    """
    Find all neighbors of an object.
    
    Args:
        object_id: Object to query
        graph: Adjacency graph
    
    Returns:
        Set of neighboring object IDs
    
    Example:
        >>> graph = {"wall_01": {"wall_02", "wall_03"}}
        >>> neighbors = find_neighbors("wall_01", graph)
        >>> len(neighbors)
        2
    """
    return graph.get(object_id, set())


def is_connected(
    obj_a: ObjectId,
    obj_b: ObjectId,
    graph: Dict[ObjectId, Set[ObjectId]]
) -> bool:
    """
    Check if two objects are connected (directly or indirectly).
    
    Args:
        obj_a: First object ID
        obj_b: Second object ID
        graph: Adjacency graph
    
    Returns:
        True if objects are in the same connected component
    
    Example:
        >>> graph = {
        ...     "wall_01": {"wall_02"},
        ...     "wall_02": {"wall_01", "wall_03"},
        ...     "wall_03": {"wall_02"},
        ... }
        >>> is_connected("wall_01", "wall_03", graph)
        True
    
    Use Case:
        Check if two objects are structurally connected.
    """
    if obj_a not in graph or obj_b not in graph:
        return False
    
    if obj_a == obj_b:
        return True
    
    # BFS to check connectivity
    visited: Set[ObjectId] = set()
    queue: List[ObjectId] = [obj_a]
    visited.add(obj_a)
    
    while queue:
        current = queue.pop(0)
        
        if current == obj_b:
            return True
        
        for neighbor in graph.get(current, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False


def get_object_degree(
    object_id: ObjectId,
    graph: Dict[ObjectId, Set[ObjectId]]
) -> int:
    """
    Get the degree (number of connections) of an object.
    
    Args:
        object_id: Object to query
        graph: Adjacency graph
    
    Returns:
        Number of connected objects
    
    Example:
        >>> graph = {"wall_01": {"wall_02", "wall_03"}}
        >>> get_object_degree("wall_01", graph)
        2
    """
    return len(graph.get(object_id, set()))
