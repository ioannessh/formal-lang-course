from project.utils.converters import NfaAsMatrix
from scipy.sparse import kron, dok_matrix


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
