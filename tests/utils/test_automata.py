from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from project.utils.automata import *


def test_cross_automata():
    nfa1 = NondeterministicFiniteAutomaton()
    nfa1.add_transitions(
        [(0, "a", 1), (1, "a", 2), (2, "a", 3), (3, "a", 4), (0, "b", 2), (2, "c", 4)]
    )
    nfa1.add_start_state(0)
    nfa1.add_final_state(3)
    nfa1.add_final_state(4)

    nfa2 = NondeterministicFiniteAutomaton()
    nfa2.add_transitions(
        [
            (0, "b", 1),
            (1, "b", 4),
            (1, "b", 2),
            (2, "b", 3),
            (3, "b", 4),
            (1, "a", 3),
            (1, "c", 4),
        ]
    )
    nfa2.add_start_state(0)
    nfa2.add_final_state(3)
    nfa2.add_final_state(4)

    nfa = cross_automata(nfa1, nfa2)
    test = [
        ["a", "a", "a", "a"],
        ["a", "a", "a"],
        ["a", "a", "c"],
        ["b", "a", "a"],
        ["b", "c"],
        ["b", "b", "b", "b"],
        ["b", "a"],
        ["b", "b", "b"],
        ["b", "a", "b"],
        ["b", "b"],
    ]

    for i in test:
        assert (nfa1.accepts(i) and nfa2.accepts(i)) == nfa.accepts(i)
