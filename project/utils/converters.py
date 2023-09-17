from networkx import MultiDiGraph
from pyformlang.finite_automaton import EpsilonNFA, NondeterministicFiniteAutomaton, DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex


def convert_regex_to_minimal_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    return regex.to_epsilon_nfa().to_deterministic().minimize()


def convert_nfa_to_graph(graph: MultiDiGraph, start_nodes: set = None,
                         end_nodes: set = None) -> NondeterministicFiniteAutomaton:
    enfa = EpsilonNFA.from_networkx(graph)
    if start_nodes is None:
        start_nodes = graph.nodes
    for i in start_nodes:
        enfa.start_states.add(i)
    if end_nodes is None:
        end_nodes = graph.nodes
    for i in end_nodes:
        enfa.final_states.add(i)
    return enfa.remove_epsilon_transitions()
