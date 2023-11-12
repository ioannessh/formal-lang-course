from typing import Iterable

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import (
    EpsilonNFA,
    NondeterministicFiniteAutomaton,
    DeterministicFiniteAutomaton,
    State,
)


class subAutomaton:
    def __init__(
        self, variable: Variable = None, dfa: DeterministicFiniteAutomaton = None
    ):
        self._variable = variable
        self._dfa = dfa

    def __eq__(self, other: "subAutomaton"):
        return self._variable == other._variable and self._dfa.is_equivalent_to(
            other._dfa
        )

    @property
    def dfa(self) -> DeterministicFiniteAutomaton:
        return self._dfa

    @property
    def variable(self) -> Variable:
        return self._variable

    def minimize(self) -> "subAutomaton":
        return subAutomaton(self._variable, self._dfa.minimize())


class RecursiveStateMachine:
    def __init__(self, start_symbol: Variable, sub_automatons: Iterable[subAutomaton]):
        self._start_symbol = start_symbol
        self._sub_automatons = sub_automatons

    @property
    def start_symbol(self):
        return self._start_symbol

    @property
    def sub_automatons(self):
        return self._sub_automatons

    def set_start_symbol(self, start_symbol: Variable):
        self._start_symbol = start_symbol

    def minimize(self) -> "RecursiveStateMachine":
        return RecursiveStateMachine(
            self._start_symbol, [i.minimize() for i in self._sub_automatons]
        )
