import pytest
from project.grammars.extended_contex_free_grammar import ECFG
from project.grammars.recursive_state_machine import *
from project.utils.converters import convert_ecfg_to_rsm


@pytest.mark.parametrize(
    "ecfg_text", ["", "S -> epsilon", "S -> A A* c* B*\nA -> a d*\nB -> b*"]
)
def test_convert_ecfg_to_rsm(ecfg_text):
    ecfg = ECFG.from_text(ecfg_text)
    rsm = convert_ecfg_to_rsm(ecfg)
    minimized_rsm = rsm.minimize()
    act_automatons = rsm.sub_automatons
    exp_automatons = [i.minimize() for i in rsm.sub_automatons]
    for a, e in zip(act_automatons, exp_automatons):
        assert isinstance(a, subAutomaton)
        assert isinstance(e, subAutomaton)
        assert a.dfa.is_equivalent_to(e.dfa)
