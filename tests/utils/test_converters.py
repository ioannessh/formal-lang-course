import os

import pytest

from project.utils.converters import *
from project.utils.graph import *
from project.utils.matrix import *
import networkx as nx
from pyformlang.cfg import CFG, Variable, Terminal, Production


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


def is_wcnf(wcnf: CFG):
    for i in wcnf.productions:
        if not (
            (
                len(i.body) == 2
                and i.body[0] in wcnf.variables
                and i.body[1] in wcnf.variables
            )
            or (len(i.body) == 1 and i.body[0] in wcnf.terminals)
            or len(i.body) == 0
        ):
            return False
    return True


@pytest.fixture
def default_cfg() -> CFG:
    variables = {Variable("A"), Variable("B")}
    terms = {Terminal("("), Terminal(")"), Terminal("1"), Terminal("0")}
    start_symbol = Variable("A")
    prods = {
        Production(Variable("A"), [Terminal("("), Variable("A"), Terminal(")")]),
        Production(Variable("A"), [Variable("A"), Variable("A")]),
        Production(Variable("A"), [Terminal("1"), Variable("B")]),
        Production(Variable("B"), [Terminal("1"), Variable("B")]),
        Production(Variable("B"), [Terminal("1"), Terminal("0")]),
    }
    return CFG(variables, terms, start_symbol, prods)


@pytest.fixture
def expected_wcnf() -> CFG:
    variables = {
        Variable("A"),
        Variable("B"),
        Variable("0#CNF#"),
        Variable("1#CNF#"),
        Variable("(#CNF#"),
        Variable(")#CNF#"),
        Variable("C#CNF#1"),
    }
    terms = {Terminal("("), Terminal(")"), Terminal("1"), Terminal("0")}
    start_symbol = Variable("A")
    prods = {
        Production(Variable("A"), [Variable("A"), Variable("A")]),
        Production(Variable("A"), [Variable("1#CNF#"), Variable("B")]),
        Production(Variable("A"), []),
        Production(Variable("B"), [Variable("1#CNF#"), Variable("0#CNF#")]),
        Production(Variable("B"), [Variable("1#CNF#"), Variable("B")]),
        Production(Variable("A"), [Variable("(#CNF#"), Variable("C#CNF#1")]),
        Production(Variable("C#CNF#1"), [Variable("A"), Variable(")#CNF#")]),
        Production(Variable("0#CNF#"), [Terminal("0")]),
        Production(Variable("(#CNF#"), [Terminal("(")]),
        Production(Variable("1#CNF#"), [Terminal("1")]),
        Production(Variable(")#CNF#"), [Terminal(")")]),
    }
    return CFG(variables, terms, start_symbol, prods)


def test_assert_cfg_with_expected_wcnf(default_cfg, expected_wcnf):
    actual_wcnf = convert_cfg_to_wcnf(default_cfg)
    assert is_wcnf(actual_wcnf)
    assert (
        len(set(actual_wcnf.productions).difference(set(expected_wcnf.productions)))
        == 0
    )
    assert set(actual_wcnf.variables) == set(expected_wcnf.variables)
    assert set(actual_wcnf.terminals) == set(expected_wcnf.terminals)
    assert actual_wcnf.start_symbol == expected_wcnf.start_symbol


@pytest.mark.parametrize(
    "start_symbol,cfg_text",
    [
        ("S", "S -> epsilon"),
        ("S", "S -> a A b B\nA -> c\n B -> d\n S -> epsilon"),
        ("A", "A -> A A\nA -> \nB -> a b\nA -> a B\nA -> ( A )\nB -> a B"),
        ("A", "A -> a A a A a A\nA -> b\n A -> c d\nA -> epsilon"),
    ],
)
def test_convert_cfg_to_wcnf(start_symbol: str, cfg_text: str):
    cfg = CFG.from_text(cfg_text, start_symbol)
    wcnf = convert_cfg_to_wcnf(cfg)
    assert is_wcnf(wcnf)
