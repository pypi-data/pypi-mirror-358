from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar, Callable, Iterable, TYPE_CHECKING

from spellbind.values import Value, OneToOneValue, SimpleVariable, Constant, \
    ManyToSameValue, ThreeToOneValue

if TYPE_CHECKING:
    from spellbind.int_values import IntValue, IntConstant  # pragma: no cover


StrLike = str | Value[str]

_S = TypeVar('_S')
_T = TypeVar('_T')
_U = TypeVar('_U')
_JOIN_FUNCTIONS: dict[str, Callable[[Iterable[str]], str]] = {}


def _get_join_function(separator: str) -> Callable[[Iterable[str]], str]:
    try:
        return _JOIN_FUNCTIONS[separator]
    except KeyError:
        def join_function(values: Iterable[str]) -> str:
            return separator.join(values)
        _JOIN_FUNCTIONS[separator] = join_function
        return join_function


_join_strs = _get_join_function("")


class StrValue(Value[str], ABC):
    def __add__(self, other: StrLike) -> StrValue:
        return StrValue.derive_from_many(_join_strs, self, other, is_associative=True)

    def __radd__(self, other: StrLike) -> StrValue:
        return StrValue.derive_from_many(_join_strs, other, self, is_associative=True)

    @property
    def length(self) -> IntValue:
        from spellbind.int_values import IntValue
        str_length: Callable[[str], int] = len
        return IntValue.derive_from_one(str_length, self)

    def to_str(self) -> StrValue:
        return self

    @classmethod
    def derive_from_three(cls, transformer: Callable[[_S, _T, _U], str],
                          first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> StrValue:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToStrValue.create,
            create_constant=StrConstant.of,
        )

    @classmethod
    def derive_from_many(cls, transformer: Callable[[Iterable[str]], str], *values: StrLike, is_associative: bool = False) -> StrValue:
        return Value.derive_from_many_with_factory(
            transformer,
            *values,
            create_value=ManyStrsToStrValue.create,
            create_constant=StrConstant.of,
            is_associative=is_associative,
        )


def concatenate(*values: StrLike) -> StrValue:
    return StrValue.derive_from_many(_join_strs, *values, is_associative=True)


def join(separator: str = "", *values: StrLike) -> StrValue:
    return StrValue.derive_from_many(_get_join_function(separator), *values, is_associative=True)


class OneToStrValue(OneToOneValue[_S, str], StrValue, Generic[_S]):
    pass


class StrConstant(Constant[str], StrValue):
    _cache: dict[str, StrConstant] = {}

    @classmethod
    def of(cls, value: str, cache: bool = False) -> StrConstant:
        try:
            return cls._cache[value]
        except KeyError:
            constant = StrConstant(value)
            if cache:
                cls._cache[value] = constant
            return constant

    @property
    def length(self) -> IntConstant:
        from spellbind.int_values import IntConstant
        return IntConstant.of(len(self.value))


EMPTY_STRING = StrConstant.of("")

for _number_value in [*range(10)]:
    StrConstant.of(str(_number_value), cache=True)

for _alpha_value in "abcdefghijklmnopqrstuvwxyz":
    StrConstant.of(_alpha_value, cache=True)
    StrConstant.of(_alpha_value.upper(), cache=True)

for _special_char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/":
    StrConstant.of(_special_char, cache=True)


class StrVariable(SimpleVariable[str], StrValue):
    pass


class ManyStrsToStrValue(ManyToSameValue[str], StrValue):
    @staticmethod
    def create(transformer: Callable[[Iterable[str]], str], values: Iterable[StrLike]) -> StrValue:
        return ManyStrsToStrValue(transformer, *values)


class ThreeToStrValue(ThreeToOneValue[_S, _T, _U, str], StrValue, Generic[_S, _T, _U]):
    @staticmethod
    def create(transformer: Callable[[_S, _T, _U], str],
               first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> StrValue:
        return ThreeToStrValue(transformer, first, second, third)


class ToStrValue(OneToOneValue[Any, str], StrValue):
    def __init__(self, value: Value[Any]):
        super().__init__(str, value)
