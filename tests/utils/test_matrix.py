import pytest
from project.utils.matrix import *


def test_transitive_closure():
    matrix = dok_matrix((6, 6), dtype=bool)
    transitions = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 2]]
    for i in transitions:
        matrix[i[0], i[1]] = True
    tc_matrix = transitive_closure(matrix)
    ans = [
        [0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
    ]
    for i in range(6):
        for j in range(6):
            assert tc_matrix[i, j] == ans[i][j]
