import os

import pytest
import filecmp
from project.utils.graph import *


def test_graph_data():
    stat = get_graph_data(load_graph("bzip"))
    assert stat.num_of_nodes == 632
    assert stat.num_of_edges == 556
    assert stat.set_of_labels == set({"d", "a"})


def test_draw_graph():
    path = os.path.dirname(os.path.realpath(__file__))
    actual_file = f"{path}/actual_graph.dot"
    expected_file = f"{path}/expected_graph.dot"
    draw_graph(build_two_cycles_graph(2, 3, ("a", "b")), actual_file)
    assert filecmp.cmp(expected_file, actual_file)


def test_regular_request():
    regex = Regex("b b a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    g_nfa = convert_graph_to_nfa(graph, {0}, {0, 3, 4, 5})
    rr = regular_request(graph, {0}, {0, 2, 3, 4}, regex)
    ans = {(0, 0), (0, 2), (0, 3), (0, 4)}
    assert rr == ans
