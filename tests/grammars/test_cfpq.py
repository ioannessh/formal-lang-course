import pytest
from cfpq_data import labeled_cycle_graph
from pyformlang.cfg import CFG

from project.grammars.cfpq import cfpq_matrix, hellings, matrix, cfpq_hellings
from project.utils.graph import build_two_cycles_graph


@pytest.mark.parametrize(
    "cfg_text,graph,exp_set",
    [
        (
            "S -> epsilon",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 0), (1, "S", 1), (2, "S", 2)},
        ),
        (
            "S -> a",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 1), (1, "S", 2), (2, "S", 0)},
        ),
        (
            "S -> a epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(1, "S", 0), (0, "S", 1)},
        ),
        (
            "S -> S1 B\nS1 -> A A\nA -> a\nB -> b",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {
                (0, "S", 2),
                (0, "A", 1),
                (2, "B", 3),
                (1, "A", 0),
                (0, "B", 2),
                (3, "B", 0),
                (1, "S1", 1),
                (0, "S1", 0),
            },
        ),
    ],
)
def test_hellings(cfg_text, graph, exp_set):
    assert hellings(CFG.from_text(cfg_text), graph) == exp_set


@pytest.mark.parametrize(
    "cfg_text,graph,exp_set",
    [
        (
            "S -> epsilon",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 0), (1, "S", 1), (2, "S", 2)},
        ),
        (
            "S -> a",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 1), (1, "S", 2), (2, "S", 0)},
        ),
        (
            "S -> a epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(1, "S", 0), (0, "S", 1)},
        ),
        (
            "S -> S1 B\nS1 -> A A\nA -> a\nB -> b",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {
                (0, "S", 2),
                (0, "A", 1),
                (2, "B", 3),
                (1, "A", 0),
                (0, "B", 2),
                (3, "B", 0),
                (1, "S1", 1),
                (0, "S1", 0),
            },
        ),
    ],
)
def test_matrix(cfg_text, graph, exp_set):
    assert matrix(CFG.from_text(cfg_text), graph) == exp_set


@pytest.mark.parametrize(
    "cfg_text,graph,exp_set",
    [
        (
            "S -> epsilon",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 0), (1, "S", 1), (2, "S", 2)},
        ),
        (
            "S -> a",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 1), (1, "S", 2), (2, "S", 0)},
        ),
        (
            "S -> a S | epsilon",
            labeled_cycle_graph(3, "a"),
            {
                (0, "S", 0),
                (0, "S", 1),
                (0, "S", 2),
                (1, "S", 1),
                (1, "S", 2),
                (1, "S", 0),
                (2, "S", 2),
                (2, "S", 1),
                (2, "S", 0),
            },
        ),
        (
            "S -> a a A\nA -> b A | epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(0, "S", 3), (1, "S", 1), (0, "S", 0), (0, "S", 2)},
        ),
        (
            "S -> A B\nA -> a a\nB -> b B | epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(1, "S", 1), (0, "S", 2), (0, "S", 3), (0, "S", 0)},
        ),
    ],
)
def test_context_free_path_querying_hellings(cfg_text, graph, exp_set):
    assert cfpq_hellings(CFG.from_text(cfg_text), graph) == exp_set
    new_exp_set = {(v, t, u) for v, t, u in exp_set if v == 0 and u == 2}
    assert cfpq_hellings(CFG.from_text(cfg_text), graph, {0}, {2}) == new_exp_set


@pytest.mark.parametrize(
    "cfg_text,graph,exp_set",
    [
        (
            "S -> epsilon",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 0), (1, "S", 1), (2, "S", 2)},
        ),
        (
            "S -> a",
            labeled_cycle_graph(3, "a"),
            {(0, "S", 1), (1, "S", 2), (2, "S", 0)},
        ),
        (
            "S -> a S | epsilon",
            labeled_cycle_graph(3, "a"),
            {
                (0, "S", 0),
                (0, "S", 1),
                (0, "S", 2),
                (1, "S", 1),
                (1, "S", 2),
                (1, "S", 0),
                (2, "S", 2),
                (2, "S", 1),
                (2, "S", 0),
            },
        ),
        (
            "S -> a a A\nA -> b A | epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(0, "S", 3), (1, "S", 1), (0, "S", 0), (0, "S", 2)},
        ),
        (
            "S -> A B\nA -> a a\nB -> b B | epsilon",
            build_two_cycles_graph(1, 2, ("a", "b")),
            {(1, "S", 1), (0, "S", 2), (0, "S", 3), (0, "S", 0)},
        ),
    ],
)
def test_context_free_path_querying_matrix(cfg_text, graph, exp_set):
    assert cfpq_matrix(CFG.from_text(cfg_text), graph) == exp_set
    new_exp_set = {(v, t, u) for v, t, u in exp_set if v == 0 and u == 2}
    assert cfpq_matrix(CFG.from_text(cfg_text), graph, {0}, {2}) == new_exp_set
