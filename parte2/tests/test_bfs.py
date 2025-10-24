import pytest
from graphs.bfs import bfs

@pytest.fixture
def sample_graph():
    return {
        'A': [('B', 1, ''), ('C', 1, '')],
        'B': [('D', 1, '')],
        'C': [('D', 1, ''), ('A', 1, '')],
        'D': []
    }

def test_bfs_levels(sample_graph):
    result = bfs(sample_graph, 'A')
    assert result["levels"]['A'] == 0
    assert result["levels"]['B'] == 1
    assert result["levels"]['D'] >= 1

def test_bfs_cycle_detection(sample_graph):
    result = bfs(sample_graph, 'A')
    assert len(result["cycles"]) >= 1
