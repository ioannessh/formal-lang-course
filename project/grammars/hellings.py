from networkx import MultiDiGraph
from pyformlang.cfg import CFG
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
