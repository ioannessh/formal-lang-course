import os

from project.utils.converters import *
from project.utils.graph import *
from project.utils.matrix import *
import networkx as nx


def test_regex_to_dfa():
    g = convert_regex_to_minimal_dfa(Regex("ab"))
    assert g.is_deterministic()


def test_final_states_in_nfa_by_graph():
    g = load_graph("bzip")
    nfa = convert_graph_to_nfa(g)
    for node in g.nodes:
        assert nfa.is_final_state(node)


def test_isomorphic_nfa_and_graph():
    path = os.path.dirname(os.path.realpath(__file__))
    actual_graph = build_two_cycles_graph(2, 3, ("a", "b"))
    nfa = convert_graph_to_nfa(actual_graph, set(), set())
    expected_graph = nfa.to_networkx()
    assert nx.is_isomorphic(actual_graph, expected_graph)


def test_convert_nfa_to_matrix():
    nfa = NondeterministicFiniteAutomaton()
    transitions = [
        (0, "a", 1),
        (1, "a", 2),
        (2, "a", 3),
        (3, "a", 4),
        (0, "b", 2),
        (2, "c", 4),
    ]

    start_states = {0}
    final_states = {3, 4}
    nfa.add_transitions(transitions)
    for i in start_states:
        nfa.add_start_state(i)
    for i in final_states:
        nfa.add_final_state(i)
    matrix = convert_nfa_to_matrix(nfa)

    for i in transitions:
        assert matrix.matrices[i[1]][i[0], i[2]]
        matrix.matrices[i[1]][i[0], i[2]] = False

    for q in matrix.matrices.keys():
        assert 0 == matrix.matrices[q].count_nonzero()

    assert matrix.start_states == start_states
    assert matrix.final_states == final_states


def test_convert_matrix_to_nfa():
    nfa1 = NondeterministicFiniteAutomaton()
    nfa1.add_transitions(
        [
            ("a", "a", "b"),
            ("b", "a", "c"),
            ("c", "a", "d"),
            ("d", "a", "e"),
            ("a", "b", "c"),
            ("c", "c", "e"),
        ]
    )
    nfa1.add_start_state("a")
    nfa1.add_final_state("d")
    nfa1.add_final_state("e")
    m = convert_nfa_to_matrix(nfa1)
    nfa2 = convert_matrix_to_nfa(m)
    assert nfa1.to_dict() == nfa2.to_dict()
