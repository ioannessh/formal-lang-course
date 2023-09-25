import cfpq_data
import networkx

from cfpq_data import *
from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from project.utils.converters import *
from project.utils.automata import *
from project.utils.matrix import *


class GraphData:
    num_of_nodes: int
    num_of_edges: int
    set_of_labels: set

    def __init__(self, nodes: int, edges: int, labels: set):
        self.num_of_nodes = nodes
        self.num_of_edges = edges
        self.set_of_labels = labels


def load_graph(name: str) -> MultiDiGraph:
    bzip_graph = cfpq_data.graph_from_csv(path=(cfpq_data.download(name)))
    return bzip_graph


def get_graph_data(graph: MultiDiGraph) -> GraphData:
    return GraphData(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        set(i for _, _, i in graph.edges.data("label")),
    )


def build_two_cycles_graph(
    n: int, m: int, label_names: tuple[str, str]
) -> MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=label_names)


def draw_graph(graph: MultiDiGraph, path: str):
    networkx.drawing.nx_pydot.to_pydot(graph).write(path)


def regular_request(
    graph: MultiDiGraph, start_node: set, end_node: set, regex: Regex
) -> set:
    graph_nfa = convert_graph_to_nfa(graph, start_node, end_node)
    regex_dfa = convert_regex_to_minimal_dfa(regex)
    graph_matrix = convert_nfa_to_matrix(graph_nfa)
    regex_matrix = convert_nfa_to_matrix(regex_dfa)
    crossed_matrix = cross_matrices(regex_matrix, graph_matrix)
    union_matrix = dok_matrix(
        (crossed_matrix.cnt_of_states, crossed_matrix.cnt_of_states), dtype=bool
    )
    for i in crossed_matrix.matrices.values():
        union_matrix = union_matrix + i
    tc_matrix = transitive_closure(union_matrix)

    states_arr = [State("0") for _ in range(graph_matrix.cnt_of_states)]
    for state in graph_matrix.indexes:
        index = graph_matrix.indexes[state]
        states_arr[index] = state

    ret = set()
    for index_from, index_to in zip(*tc_matrix.nonzero()):
        state_from = states_arr[index_from % graph_matrix.cnt_of_states]
        state_to = states_arr[index_to % graph_matrix.cnt_of_states]
        if (
            index_from in crossed_matrix.start_states
            and index_to in crossed_matrix.final_states
        ):
            ret.add((state_from, state_to))
    return ret
