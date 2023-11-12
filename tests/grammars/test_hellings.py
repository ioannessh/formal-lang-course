import pytest
from cfpq_data import labeled_cycle_graph
from pyformlang.cfg import CFG

from project.grammars.hellings import hellings
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
