import click
import os
import sys
import json
import yaml
from typing import Optional, List, Dict, Set
from pathlib import Path

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from blenpc.engine_v2.core import (
    Engine, 
    GridState, 
    detect_rooms, 
    get_room_stats, 
    build_structural_graph, 
    get_graph_stats
)

def print_banner():
    click.secho("""
    ██████╗ ██╗     ███████╗███╗   ██╗██████╗  ██████╗    ██╗   ██╗██████╗ 
    ██╔══██╗██║     ██╔════╝████╗  ██║██╔══██╗██╔════╝    ██║   ██║╚════██╗
    ██████╔╝██║     █████╗  ██╔██╗ ██║██████╔╝██║         ██║   ██║ █████╔╝
    ██╔══██╗██║     ██╔══╝  ██║╚██╗██║██╔═══╝ ██║         ╚██╗ ██╔╝██╔═══╝ 
    ██████╔╝███████╗███████╗██║ ╚████║██║     ╚██████╗     ╚████╔╝ ███████╗
    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝      ╚═════╝      ╚═══╝  ╚══════╝
    """, fg="cyan", bold=True)
    click.secho("    --- Engine V2 CLI - Modern, Immutable, Deterministic ---", fg="white", dim=True)

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """BlenPC Engine V2 CLI - Spatial Intelligence & Grid Management"""
    pass

@cli.command()
@click.option('--width', '-w', type=int, default=10, help="Grid width (max x)")
@click.option('--depth', '-d', type=int, default=10, help="Grid depth (max y)")
@click.option('--z', '-z', type=int, default=0, help="Z-level to analyze")
@click.option('--min-size', type=int, default=4, help="Minimum room size")
@click.option('--spec', type=click.Path(exists=True), help="Path to grid state JSON")
def analyze(width, depth, z, min_size, spec):
    """Analyze a grid state (Room detection, Structural graph)."""
    print_banner()
    
    if spec:
        with open(spec, 'r') as f:
            data = json.load(f)
            # Simple conversion if needed, assuming data is dict of cell:obj
            cells = {tuple(map(int, k.strip("()").split(","))): v for k, v in data.items()}
            grid = GridState(_cells=cells)
    else:
        click.secho("No spec file provided. Using empty grid.", fg="yellow")
        grid = GridState.empty()

    # 1. Room Detection
    click.secho("\n🔍 [1/2] Room Detection Analysis", fg="green", bold=True)
    rooms = detect_rooms(grid, z_level=z, bounds=(width, depth), min_size=min_size)
    stats = get_room_stats(rooms)
    
    click.echo(f"  • Rooms Found: {stats['room_count']}")
    click.echo(f"  • Total Room Area: {stats['total_cells']} cells")
    if stats['room_count'] > 0:
        click.echo(f"  • Avg Room Size: {stats['avg_room_size']:.1f} cells")
        click.echo(f"  • Max Room Size: {stats['max_room_size']} cells")

    # 2. Structural Graph
    click.secho("\n🏗️ [2/2] Structural Graph Analysis", fg="green", bold=True)
    graph = build_structural_graph(grid)
    g_stats = get_graph_stats(graph)
    
    click.echo(f"  • Unique Objects: {g_stats['node_count']}")
    click.echo(f"  • Structural Connections: {g_stats['edge_count']}")
    click.echo(f"  • Isolated Objects: {g_stats['isolated_count']}")
    if g_stats['node_count'] > 0:
        click.echo(f"  • Max Connectivity: {g_stats['max_degree']}")

    click.secho("\n✅ Analysis Complete.", fg="cyan", bold=True)

@cli.command()
@click.argument('commands_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help="Output state JSON file")
def run(commands_file, output):
    """Run a sequence of engine commands from a file."""
    print_banner()
    
    with open(commands_file, 'r') as f:
        if commands_file.endswith(('.yaml', '.yml')):
            cmds = yaml.safe_load(f)
        else:
            cmds = json.load(f)
            
    engine = Engine()
    click.echo(f"Executing {len(cmds)} commands...")
    
    success_count = 0
    with click.progressbar(cmds, label='Processing') as bar:
        for cmd in bar:
            action = cmd.get('action')
            obj_id = cmd.get('id')
            footprint = cmd.get('footprint')
            
            try:
                if action == 'place':
                    # Convert list of lists to frozenset of tuples
                    fp = frozenset(tuple(c) for c in footprint)
                    engine.place(obj_id, fp)
                elif action == 'remove':
                    engine.remove(obj_id)
                elif action == 'undo':
                    engine.undo()
                elif action == 'redo':
                    engine.redo()
                success_count += 1
            except Exception as e:
                click.secho(f"\nError in command {action} {obj_id}: {str(e)}", fg="red")

    click.secho(f"\n✓ Finished: {success_count}/{len(cmds)} commands successful.", fg="green")
    
    if output:
        # Serialize grid state
        state_dict = {str(k): v for k, v in engine.state._cells.items()}
        with open(output, 'w') as f:
            json.dump(state_dict, f, indent=2)
        click.echo(f"Final state saved to: {output}")

@cli.command()
def test():
    """Run Engine V2 test suite."""
    import pytest
    print_banner()
    click.secho("Running Engine V2 Test Suite...", fg="yellow")
    
    test_path = os.path.join(os.path.dirname(__file__), "engine_v2", "tests")
    pytest.main([test_path, "-v"])

@cli.command()
def bench():
    """Run performance benchmarks."""
    import time
    print_banner()
    click.secho("Running Performance Benchmarks...", fg="yellow")
    
    engine = Engine(enable_history=False)
    
    # Benchmark 1: Placement
    start = time.time()
    for i in range(1000):
        engine.place(f"obj_{i}", frozenset({(i, 0, 0)}))
    end = time.time()
    click.echo(f"  • 1000 Placements: {(end-start)*1000:.2f}ms")
    
    # Benchmark 2: Room Detection
    # Create a 50x50 grid with walls
    grid_cells = {}
    for x in range(50):
        grid_cells[(x, 0, 0)] = "wall"
        grid_cells[(x, 49, 0)] = "wall"
    for y in range(50):
        grid_cells[(0, y, 0)] = "wall"
        grid_cells[(49, y, 0)] = "wall"
    grid = GridState(_cells=grid_cells)
    
    start = time.time()
    detect_rooms(grid, bounds=(50, 50))
    end = time.time()
    click.echo(f"  • Room Detection (50x50): {(end-start)*1000:.2f}ms")

if __name__ == '__main__':
    cli()
