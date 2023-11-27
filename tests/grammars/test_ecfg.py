from typing import Dict

import pytest
from pyformlang.cfg import CFG, Variable, Terminal, Production
from project.grammars.extended_contex_free_grammar import *


def regex_eq(a: Regex, b: Regex) -> bool:
    from project.utils.converters import convert_regex_to_minimal_dfa

    return convert_regex_to_minimal_dfa(a).is_equivalent_to(
        convert_regex_to_minimal_dfa(b)
    )


@pytest.mark.parametrize("ecfg_text", ["S -> $\nS -> a", "S -> A B A -> a\nB -> b"])
def test_error_raises(ecfg_text: str):
    with pytest.raises(ECFGException):
        ECFG.from_text(ecfg_text)


@pytest.mark.parametrize(
    "ecfg_text,exp_ecfg_prod,exp_vars",
    [
        ("S -> $", {Variable("S"): Regex("$")}, {Variable("S")}),
        (
            "S -> a S b S | $",
            {Variable("S"): Regex("( a S b S ) | $")},
            {Variable("S")},
        ),
        (
            "S -> A B\nA -> a\nB -> b",
            {
                Variable("S"): Regex("A B"),
                Variable("B"): Regex("b"),
                Variable("A"): Regex("a"),
            },
            {Variable("S"), Variable("A"), Variable("B")},
        ),
    ],
)
def test_ecfg_from_text(
    ecfg_text: str,
    exp_ecfg_prod: Dict[(Variable, Regex)],
    exp_vars: AbstractSet[Variable],
):
    ecfg = ECFG.from_text(ecfg_text)
    assert set(ecfg.variables) == set(exp_ecfg_prod)
    assert all(
        (
            (exp_ecfg_prod.get(prod.head) is not None)
            and regex_eq(prod.body, exp_ecfg_prod[prod.head])
        )
        for prod in ecfg.productions
    )
