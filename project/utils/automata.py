from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from project.utils.converters import *
from project.utils.matrix import *


def cross_automata(
    nfa1: NondeterministicFiniteAutomaton, nfa2: NondeterministicFiniteAutomaton
) -> NondeterministicFiniteAutomaton:
    matrix = cross_matrices(convert_nfa_to_matrix(nfa1), convert_nfa_to_matrix(nfa2))
    return convert_matrix_to_nfa(matrix)
