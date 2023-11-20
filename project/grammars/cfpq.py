from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import dok_matrix

from project.utils.converters import convert_cfg_to_wcnf


def hellings(cfg: CFG, graph: MultiDiGraph) -> set:
    wcnf = convert_cfg_to_wcnf(cfg)
    eps = {n.head.value for n in wcnf.productions if len(n.body) == 0}
    terms_prod = {p for p in wcnf.productions if len(p.body) == 1}
    vars_prod = {p for p in wcnf.productions if len(p.body) == 2}
    r = {(v, e, v) for v in range(graph.number_of_nodes()) for e in eps}
    r |= {
        (v, n.head.value, u)
        for v, u, t in graph.edges(data=True)
        for n in terms_prod
        if n.body[0].value == t["label"]
    }
    m = r.copy()

    while len(m) > 0:
        v, ni, u = m.pop()
        tmp = set()
        for v1, nj, vt in r:
            if vt == v:
                for pk in vars_prod:
                    if (
                        pk.body[0] == nj
                        and pk.body[1] == ni
                        and (v1, pk.head.value, u) not in r
                    ):
                        tmp.add((v1, pk.head.value, u))
        r |= tmp
        m |= tmp
        tmp.clear()
        for ut, nj, v1 in r:
            if ut == u:
                for pk in vars_prod:
                    if (
                        pk.body[0] == ni
                        and pk.body[1] == nj
                        and (v, pk.head.value, v1) not in r
                    ):
                        tmp.add((v, pk.head.value, v1))
        r |= tmp
        m |= tmp
    return r


def matrix(cfg: CFG, graph: MultiDiGraph) -> set:
    wcnf = convert_cfg_to_wcnf(cfg)
    eps = {n.head.value for n in wcnf.productions if len(n.body) == 0}
    terms_prod = {p for p in wcnf.productions if len(p.body) == 1}
    vars_prod = {p for p in wcnf.productions if len(p.body) == 2}
    n = graph.number_of_nodes()
    t_matrix = {v.value: dok_matrix((n, n), dtype=bool) for v in wcnf.variables}
    for i, j, x in graph.edges(data=True):
        for t in terms_prod:
            if t.body[0].value == x["label"]:
                t_matrix[t.head.value][i, j] = True
    for i in range(n):
        for v in eps:
            t_matrix[v][i, i] = True
    flag = True
    while flag:
        flag = False
        for v in vars_prod:
            old_nnz = t_matrix[v.head.value].nnz
            t_matrix[v.head.value] += (
                t_matrix[v.body[0].value] @ t_matrix[v.body[1].value]
            )
            flag |= old_nnz != t_matrix[v.head.value].nnz
    ret = set()
    for var, mx in t_matrix.items():
        for i, j in zip(*mx.nonzero()):
            ret.add((i, var, j))
    return ret


def cfpq_hellings(
    cfg: CFG,
    graph: MultiDiGraph,
    start_nodes: set = None,
    end_nodes: set = None,
    start_var: Variable = Variable("S"),
) -> set:
    cfg._start_symbol = start_var
    res = {
        (v, h, u)
        for v, h, u in hellings(cfg, graph)
        if (start_nodes is None or v in start_nodes)
        and (end_nodes is None or u in end_nodes)
        and h == start_var.value
    }
    return res


def cfpq_matrix(
    cfg: CFG,
    graph: MultiDiGraph,
    start_nodes: set = None,
    end_nodes: set = None,
    start_var: Variable = Variable("S"),
) -> set:
    cfg._start_symbol = start_var
    res = {
        (v, h, u)
        for v, h, u in matrix(cfg, graph)
        if (start_nodes is None or v in start_nodes)
        and (end_nodes is None or u in end_nodes)
        and h == start_var.value
    }
    return res
