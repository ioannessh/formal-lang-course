from pyformlang.cfg import CFG, Variable


def read_cfg_from_file(filename: str, start_node: str = "S"):
    with open(filename, "r") as cfg_file:
        cfg_text = cfg_file.read()

    return CFG.from_text(cfg_text, Variable(start_node))
