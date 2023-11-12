from networkx import MultiDiGraph
from pyformlang.cfg import CFG
from pyformlang.cfg import Variable

from project.grammars.hellings import hellings


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
