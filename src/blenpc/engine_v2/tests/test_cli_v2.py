import pytest
from click.testing import CliRunner
from ...cli_v2 import cli
import json
import os

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '2.0.0' in result.output

def test_cli_bench():
    runner = CliRunner()
    result = runner.invoke(cli, ['bench'])
    assert result.exit_code == 0
    assert 'Performance Benchmarks' in result.output
    assert 'Placements' in result.output

def test_cli_run_and_analyze(tmp_path):
    runner = CliRunner()
    
    # 1. Create commands file
    cmds_file = tmp_path / "cmds.json"
    cmds = [
        {"action": "place", "id": "obj1", "footprint": [[0,0,0]]}
    ]
    cmds_file.write_text(json.dumps(cmds))
    
    # 2. Run commands
    output_file = tmp_path / "state.json"
    result = runner.invoke(cli, ['run', str(cmds_file), '--output', str(output_file)])
    assert result.exit_code == 0
    assert 'Finished: 1/1' in result.output
    assert os.path.exists(output_file)
    
    # 3. Analyze output
    result = runner.invoke(cli, ['analyze', '--spec', str(output_file), '--width', '5', '--depth', '5'])
    assert result.exit_code == 0
    assert 'Room Detection Analysis' in result.output
    assert 'Structural Graph Analysis' in result.output
    assert 'Unique Objects: 1' in result.output

def test_cli_analyze_empty():
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze'])
    assert result.exit_code == 0
    assert 'No spec file provided' in result.output
    assert 'Rooms Found: 0' in result.output
