from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    EpsilonNFA,
    NondeterministicFiniteAutomaton,
    DeterministicFiniteAutomaton,
    State,
)
from pyformlang.regular_expression import Regex
from scipy.sparse import dok_matrix
from pyformlang.cfg import CFG
from project.grammars.extended_contex_free_grammar import ECFG, ECFGProduction
from project.grammars.recursive_state_machine import RecursiveStateMachine, subAutomaton


class NfaAsMatrix:
    start_states = set()
    final_states = set()
    matrices = dict()
    indexes = dict()
    cnt_of_states = 0

    def __init__(
        self,
        start_states: set[int],
        final_states: set[int],
        matrices: dict,
        indexes: dict,
        cnt_of_states,
    ):
        self.start_states = start_states
        self.final_states = final_states
        self.matrices = matrices
        self.indexes = indexes
        self.cnt_of_states = cnt_of_states


def convert_regex_to_minimal_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    return regex.to_epsilon_nfa().to_deterministic().minimize()


def convert_graph_to_nfa(
    graph: MultiDiGraph, start_nodes: set = None, end_nodes: set = None
) -> NondeterministicFiniteAutomaton:
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


def convert_nfa_to_matrix(nfa: NondeterministicFiniteAutomaton) -> NfaAsMatrix:
    cnt_st = len(nfa.states)
    indexes = {state: index for index, state in enumerate(nfa.states)}
    matrices = dict()

    for symb in nfa.symbols:
        matrices[symb] = dok_matrix((cnt_st, cnt_st), dtype=bool)
    for state in nfa.to_dict():
        edges = nfa.to_dict()[state]
        for symb in edges:
            id_from = indexes[state]
            iter_edges = {}
            if isinstance(edges[symb], set):
                iter_edges = edges[symb]
            else:
                iter_edges = {edges[symb]}
            for i in iter_edges:
                id_to = indexes[i]
                matrices[symb][id_from, id_to] = True

    return NfaAsMatrix(
        {indexes[i] for i in nfa.start_states},
        {indexes[i] for i in nfa.final_states},
        matrices,
        indexes,
        cnt_st,
    )


def convert_matrix_to_nfa(matrix: NfaAsMatrix) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()
    states_arr = [State(0) for _ in range(matrix.cnt_of_states)]
    for state in matrix.indexes:
        index = matrix.indexes[state]
        states_arr[index] = state

    for symb in matrix.matrices:
        nonzero = matrix.matrices[symb].nonzero()
        for s_from, s_to in zip(*nonzero):
            nfa.add_transition(states_arr[s_from], symb, states_arr[s_to])

    for i in matrix.start_states:
        nfa.add_start_state(states_arr[i])
    for i in matrix.final_states:
        nfa.add_final_state(states_arr[i])

    return nfa


def convert_cfg_to_wcnf(cfg: CFG) -> CFG:
    wcnf = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )

    return CFG(
        start_symbol=cfg.start_symbol,
        productions=wcnf._decompose_productions(
            wcnf._get_productions_with_only_single_terminals()
        ),
    )


def convert_cfg_to_ecfg(cfg: CFG) -> ECFG:
    productions = dict()

    for cfg_production in cfg.productions:
        body = Regex("$")
        if cfg_production.body:
            body = Regex(" ".join([str(i.value) for i in cfg_production.body]))
        head = cfg_production.head
        if head in productions:
            productions.get(head).union(body)
        else:
            productions[head] = body
    ecfg_productions = {ECFGProduction(h, b) for h, b in productions.items()}
    return ECFG(cfg.variables, cfg.start_symbol, ecfg_productions)


def convert_ecfg_to_rsm(ecfg: ECFG) -> RecursiveStateMachine:
    return RecursiveStateMachine(
        ecfg.start_symbol,
        [
            subAutomaton(i.head, convert_regex_to_minimal_dfa(i.body))
            for i in ecfg.productions
        ],
    )
