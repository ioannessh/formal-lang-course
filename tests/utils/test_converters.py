import os

from project.utils.converters import *
from project.utils.graph_utils import *
import networkx as nx


def test_regex_to_dfa():
    g = convert_regex_to_minimal_dfa(Regex("ab"))
    assert g.is_deterministic()


def test_final_states_in_nfa_by_graph():
    g = load_graph("bzip")
    nfa = convert_nfa_to_graph(g)
    for node in g.nodes:
        assert nfa.is_final_state(node)


def test_isomorphic_nfa_and_graph():
    path = os.path.dirname(os.path.realpath(__file__))
    actual_graph = build_two_cycles_graph(2, 3, ("a", "b"))
    nfa = convert_nfa_to_graph(actual_graph, set(), set())
    expected_graph = nfa.to_networkx()
    assert nx.is_isomorphic(actual_graph, expected_graph)
