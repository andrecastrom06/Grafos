import pytest
from graphs.dfs import dfs

@pytest.fixture
def sample_graph():
    return {
        'A': [('B', 1, ''), ('C', 1, '')],
        'B': [('D', 1, '')],
        'C': [('A', 1, ''), ('D', 1, '')],
        'D': []
    }

def test_dfs_levels(sample_graph):
    result = dfs(sample_graph, 'A')
    assert result["levels"]['A'] == 0
    assert 'D' in result["levels"]

def test_dfs_cycle_detection(sample_graph):
    result = dfs(sample_graph, 'A')
    assert len(result["cycles"]) >= 1
