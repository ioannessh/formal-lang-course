from pyformlang.cfg import CFG, Variable, Terminal, Production
from project.io.read import *
import pytest


@pytest.mark.parametrize(
    "filename,cfg_text",
    [("tests/io/data/test_cfg.txt", "S -> a b | S b | a B\nB -> b | S b")],
)
def test_read_cfg(filename, cfg_text):
    actual_cfg = read_cfg_from_file(filename, "S")
    expected_cfg = CFG.from_text(cfg_text, "S")
    assert set(actual_cfg.productions) == set(expected_cfg.productions)
    assert set(actual_cfg.variables) == set(expected_cfg.variables)
    assert set(actual_cfg.terminals) == set(expected_cfg.terminals)
