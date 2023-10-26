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
    rr = regular_request(graph, {0}, {0, 2, 3, 4}, regex)
    ans = {(0, 0), (0, 2), (0, 3), (0, 4)}
    assert rr == ans

    regex = Regex("a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = regular_request(graph, {0}, {0, 2, 3, 4}, regex)
    ans = {(0, 0), (0, 2), (0, 3), (0, 4)}
    assert rr == ans


def test_regular_request_without_start_node():
    regex = Regex("b b a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = regular_request(graph, set(), {0, 2, 3, 4}, regex)
    assert rr == set()


def test_regular_request_without_end_node():
    regex = Regex("b b a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = regular_request(graph, {0}, set(), regex)
    assert rr == set()


def test_regular_request_with_many_start_node():
    regex = Regex("b b b* a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = regular_request(graph, {0, 1}, {0, 2, 3, 4}, regex)
    ans = {(0, 0), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (1, 3), (1, 4)}
    assert rr == ans

    regex = Regex("b*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = regular_request(graph, {0, 1, 4}, {0, 2, 3, 4}, regex)
    ans = {(1, 0), (0, 0)}
    assert rr == ans


def test_regular_request_empty_graph():
    regex = Regex("b b a*")
    graph = MultiDiGraph()
    rr = regular_request(graph, {0, 1, 2, 3, 4}, {0, 1, 2, 3, 4}, regex)
    assert rr == set()


def test_regular_requests_separated_ans():
    regex = Regex("b* a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = bfs_regular_request(graph, regex, {0, 1, 4}, {1, 2, 3, 4}, True)
    ans = {
        (0, 1),
        (1, 3),
        (4, 4),
        (1, 2),
        (0, 4),
        (4, 3),
        (1, 1),
        (0, 3),
        (4, 2),
        (1, 4),
        (0, 2),
        (4, 1),
    }
    assert rr == ans


def test_regular_requests_unioned_ans():
    regex = Regex("b* a*")
    graph = build_two_cycles_graph(1, 3, ("b", "a"))
    rr = bfs_regular_request(graph, regex, {0, 1, 4}, {1, 2, 3, 4}, False)
    ans = {1, 2, 3, 4}
    assert rr == ans
