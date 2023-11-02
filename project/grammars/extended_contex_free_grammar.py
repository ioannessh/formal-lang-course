from typing import AbstractSet, Iterable
from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex


class ECFGException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class ECFGProduction:
    __slots__ = ["_body", "_head", "_hash"]

    def __init__(self, head: Variable, body: Regex):
        self._head = head
        self._body = body
        self._hash = None

    @property
    def head(self) -> Variable:
        return self._head

    @property
    def body(self) -> Regex:
        return self._body

    def __eq__(self, other: "ECFGProduction"):
        return self._head == other._head and self._body == other._body

    def __str__(self):
        return f"{self._head} -> {self._body}"

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self._body) + hash(self._head)
        return self._hash


class ECFG:
    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        start_symbol: Variable = None,
        productions: Iterable[ECFGProduction] = None,
    ):
        self._variables = variables or set()
        self._start_symbol = start_symbol
        self._productions = productions or set()

    @property
    def variables(self) -> AbstractSet[Variable]:
        return self._variables

    @property
    def productions(self) -> AbstractSet[ECFGProduction]:
        return self._productions

    @property
    def start_symbol(self):
        return self._start_symbol

    def to_text(self) -> str:
        return "\n".join([str(production) for production in self._productions]) + "\n"

    @classmethod
    def from_text(cls, text: str, start_symbol=Variable("S")) -> "ECFG":
        variables = set()
        productions = set()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            cls._read_line(line, productions, variables)
        return ECFG(
            variables=variables, productions=productions, start_symbol=start_symbol
        )

    @classmethod
    def _read_line(cls, line, productions, variables):
        if len(line.split("->")) != 2:
            raise ECFGException("Expected that line has declaration of one variable")
        head_s, body_s = line.split("->")
        head = Variable(head_s.strip())
        if head in variables:
            raise ECFGException("Expected that variable have one declaration")
        variables.add(head)
        body = Regex(body_s.strip())
        productions.add(ECFGProduction(head, body))
