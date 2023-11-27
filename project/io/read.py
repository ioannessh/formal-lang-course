from pyformlang.cfg import CFG, Variable
from project.grammars.extended_contex_free_grammar import ECFG


def read_cfg_from_file(filename: str, start_node: str = "S"):
    with open(filename, "r") as cfg_file:
        cfg_text = cfg_file.read()

    return CFG.from_text(cfg_text, Variable(start_node))


def read_ecfg_from_file(filename: str, start_node: str = "S"):
    with open(filename, "r") as ecfg_file:
        ecfg_text = ecfg_file.read()

    return ECFG.from_text(ecfg_text, Variable(start_node))
