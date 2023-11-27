from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from pyformlang.finite_automaton import State
from scipy.sparse import dok_matrix, kron

from project.utils.converters import (
    convert_cfg_to_wcnf,
    convert_nfa_to_matrix,
    convert_graph_to_nfa,
    convert_ecfg_to_rsm,
    convert_cfg_to_ecfg,
    convert_cfg_to_rsm,
)
from project.utils.matrix import transitive_closure


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


def tensor(cfg: CFG, graph: MultiDiGraph) -> set:
    graph_bm = convert_nfa_to_matrix(convert_graph_to_nfa(graph))
    rsm = convert_cfg_to_rsm(cfg)
    rsm_vars = {i.variable.value for i in rsm.sub_automatons}

    def new_name(state: State, variable: Variable):
        return State(f"{state.value}#{variable.value}")

    num_of_states = sum(len(i.dfa.states) for i in rsm.sub_automatons)
    id = 0
    id_by_name = dict()
    rsm_bm = dict()
    nonterminals = dict()
    for sub_au in rsm.sub_automatons:
        final_states = set()
        for i, state in enumerate(sub_au.dfa.states):
            id_by_name[new_name(state, sub_au.variable)] = id + i
            if state in sub_au.dfa.final_states:
                final_states.add(id + i)

        sid = id_by_name[new_name(sub_au.dfa.start_state, sub_au.variable)]
        for fs in sub_au.dfa.final_states:
            fid = id_by_name[new_name(fs, sub_au.variable)]
            nonterminals.update({(sid, fid): sub_au.variable.value})

        for v, trans in sub_au.dfa.to_dict().items():
            for label, u in trans.items():
                if label not in rsm_bm:
                    rsm_bm[label] = dok_matrix(
                        (num_of_states, num_of_states), dtype=bool
                    )
                id1 = id_by_name[new_name(v, sub_au.variable)]
                id2 = id_by_name[new_name(u, sub_au.variable)]
                rsm_bm[label][id1, id2] = True

        if sub_au.dfa.states == {State("Empty")}:
            nonterminals.update({(-id, -id): sub_au.variable.value})
        id += len(sub_au.dfa.states)

    for (v, u), label in nonterminals.items():
        if v == u:
            if label not in graph_bm.matrices:
                graph_bm.matrices[label] = dok_matrix(
                    (graph_bm.cnt_of_states, graph_bm.cnt_of_states), dtype=bool
                )
            for i in range(graph_bm.cnt_of_states):
                graph_bm.matrices[label][i, i] = True

    prev_nnz = -1
    curr_nnz = sum(m.nnz for k, m in graph_bm.matrices.items())
    while curr_nnz != prev_nnz:
        kronM = dict()
        for label in graph_bm.matrices.keys() & rsm_bm.keys():
            kronM[label] = kron(graph_bm.matrices[label], rsm_bm[label], format="dok")
        if kronM.values():
            tc = transitive_closure(sum(kronM.values()))
            for i, j in zip(*tc.nonzero()):
                var = nonterminals.get((i % num_of_states, j % num_of_states))
                if var:
                    if var not in graph_bm.matrices:
                        graph_bm.matrices[var] = dok_matrix(
                            (graph_bm.cnt_of_states, graph_bm.cnt_of_states), dtype=bool
                        )
                    graph_bm.matrices[var][
                        i // num_of_states, j // num_of_states
                    ] = True
        prev_nnz = curr_nnz
        curr_nnz = sum(m.nnz for k, m in graph_bm.matrices.items())
    return {
        (v, label, u)
        for label, matrix in graph_bm.matrices.items()
        if label in rsm_vars
        for v, u in zip(*matrix.nonzero())
    }


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


def cfpq_tensor(
    cfg: CFG,
    graph: MultiDiGraph,
    start_nodes: set = None,
    end_nodes: set = None,
    start_var: Variable = Variable("S"),
) -> set:
    cfg._start_symbol = start_var
    res = {
        (v, h, u)
        for v, h, u in tensor(cfg, graph)
        if (start_nodes is None or v in start_nodes)
        and (end_nodes is None or u in end_nodes)
        and h == start_var.value
    }
    return res
