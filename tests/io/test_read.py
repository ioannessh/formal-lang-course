from pyformlang.cfg import CFG, Variable, Terminal, Production
from pyformlang.regular_expression import Regex

from project.io.read import *
import pytest


def regex_eq(a: Regex, b: Regex) -> bool:
    from project.utils.converters import convert_regex_to_minimal_dfa

    return convert_regex_to_minimal_dfa(a).is_equivalent_to(
        convert_regex_to_minimal_dfa(b)
    )


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


@pytest.mark.parametrize(
    "filename,exp_ecfg_prod,exp_ecfg_vars",
    [
        (
            "tests/io/data/test_cfg.txt",
            {
                Variable("S"): Regex("(a b) | (S b) | (a B)"),
                Variable("B"): Regex("(b) | (S b)"),
            },
            {Variable("S"), Variable("B")},
        )
    ],
)
def test_read_ecfg(filename, exp_ecfg_prod, exp_ecfg_vars):
    ecfg = read_ecfg_from_file(filename, "S")
    assert len(set(ecfg.variables).difference(exp_ecfg_prod)) == 0
    assert len(ecfg.productions) == len(exp_ecfg_prod)
    assert all(
        (
            (exp_ecfg_prod.get(prod.head) is not None)
            and regex_eq(prod.body, exp_ecfg_prod[prod.head])
        )
        for prod in ecfg.productions
    )
