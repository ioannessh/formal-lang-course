from project.utils.converters import NfaAsMatrix
from scipy.sparse import kron, dok_matrix, vstack, block_diag


def cross_matrices(left_matrix: NfaAsMatrix, right_matrix: NfaAsMatrix) -> NfaAsMatrix:
    intersection = right_matrix.matrices.keys() & left_matrix.matrices.keys()
    kron_matrices = dict()
    cnt_st = right_matrix.cnt_of_states * left_matrix.cnt_of_states
    for i in intersection:
        kron_matrices[i] = kron(left_matrix.matrices[i], right_matrix.matrices[i])

    start_states = set()
    final_states = set()
    for i in left_matrix.start_states:
        for j in right_matrix.start_states:
            start_states.add(i * right_matrix.cnt_of_states + j)
    for i in left_matrix.final_states:
        for j in right_matrix.final_states:
            final_states.add(i * right_matrix.cnt_of_states + j)
    new_indexes = dict()
    for i in range(right_matrix.cnt_of_states * left_matrix.cnt_of_states):
        new_indexes[i] = i

    return NfaAsMatrix(start_states, final_states, kron_matrices, new_indexes, cnt_st)


def transitive_closure(matrix: dok_matrix) -> dok_matrix:
    tc_matrix = matrix
    prev_cnt_nonzero = 0
    cur_cnt_nonzero = tc_matrix.count_nonzero()

    while cur_cnt_nonzero != prev_cnt_nonzero:
        tc_matrix += tc_matrix @ matrix
        prev_cnt_nonzero, cur_cnt_nonzero = cur_cnt_nonzero, tc_matrix.count_nonzero()
    return tc_matrix


def init_front(
    graph: NfaAsMatrix, regex: NfaAsMatrix, start_nodes: set = None
) -> dok_matrix:
    front = dok_matrix(
        (regex.cnt_of_states, graph.cnt_of_states + regex.cnt_of_states), dtype=bool
    )

    for i in regex.start_states:
        front[i, i] = True
        for j in start_nodes:
            front[i, regex.cnt_of_states + j] = True
    return front


def upd_front(front: dok_matrix, states_count: int) -> dok_matrix:
    new_front = dok_matrix(front.shape, dtype=bool)
    for i, j in zip(*front.nonzero()):
        id = (j % states_count) + (i // states_count) * states_count
        if j < states_count:
            new_front[id, j] = True
        else:
            new_front[id, j] += front[i, j]
    return new_front


def bfs(graph: NfaAsMatrix, regex: NfaAsMatrix, separated: bool = True) -> set:
    list_start_states = list(graph.start_states)
    if separated:
        front = vstack([init_front(graph, regex, {i}) for i in list_start_states])
    else:
        front = init_front(graph, regex, graph.start_states)

    dict_of_mul = dict()
    for i in set(graph.matrices.keys()).intersection(regex.matrices.keys()):
        dict_of_mul[i] = dok_matrix(block_diag((regex.matrices[i], graph.matrices[i])))

    used = dok_matrix(front.shape, dtype=bool)
    while True:
        prev_used = used.copy()
        for mx in dict_of_mul.values():
            if front is None:
                next_front = used @ mx
            else:
                next_front = front @ mx
            used += upd_front(next_front, regex.cnt_of_states)
        if used.count_nonzero() == prev_used.count_nonzero():
            break
        front = None

    ans = set()
    for i, j in zip(*used.nonzero()):
        if (
            not separated
            and j >= regex.cnt_of_states
            and i in regex.final_states
            and (j - regex.cnt_of_states) in graph.final_states
        ):
            ans.add(graph.indexes[j - regex.cnt_of_states])
        if (
            separated
            and j >= regex.cnt_of_states
            and (i % regex.cnt_of_states) in regex.final_states
            and (j - regex.cnt_of_states) in graph.final_states
        ):
            ans.add(
                (
                    graph.indexes[list_start_states[i // regex.cnt_of_states]],
                    graph.indexes[j - regex.cnt_of_states],
                )
            )

    return ans
