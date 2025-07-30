from __future__ import annotations

import math
import operator
from abc import ABC
from typing import Generic, Callable, Sequence, TypeVar, overload

from typing_extensions import Self
from typing_extensions import TYPE_CHECKING

from spellbind.bool_values import BoolValue
from spellbind.functions import _clamp_float, _multiply_all_floats
from spellbind.values import Value, SimpleVariable, OneToOneValue, DerivedValueBase, Constant, \
    NotConstantError, ThreeToOneValue

if TYPE_CHECKING:
    from spellbind.int_values import IntValue, IntLike  # pragma: no cover

FloatLike = Value[int] | float | Value[float]

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


_COMMUTATIVE_OPERATORS = {
    operator.add, sum, _multiply_all_floats, max, min
}


def _average_float(values: Sequence[float]) -> float:
    return sum(values) / len(values)


class FloatValue(Value[float], ABC):
    def __add__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_many(sum, self, other, is_associative=True)

    def __radd__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_many(sum, other, self, is_associative=True)

    def __sub__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.sub, self, other)

    def __rsub__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_two(operator.sub, other, self)

    def __mul__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_many(_multiply_all_floats, self, other, is_associative=True)

    def __rmul__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_many(_multiply_all_floats, other, self, is_associative=True)

    def __truediv__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.truediv, self, other)

    def __rtruediv__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_two(operator.truediv, other, self)

    def __pow__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.pow, self, other)

    def __rpow__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.pow, other, self)

    def __mod__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.mod, self, other)

    def __rmod__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_two(operator.mod, other, self)

    def __abs__(self) -> FloatValue:
        return AbsFloatValue(self)

    def floor(self) -> IntValue:
        from spellbind.int_values import IntValue
        floor_fun: Callable[[float], int] = math.floor
        return IntValue.derive_from_one(floor_fun, self)

    def ceil(self) -> IntValue:
        from spellbind.int_values import IntValue
        ceil_fun: Callable[[float], int] = math.ceil
        return IntValue.derive_from_one(ceil_fun, self)

    @overload
    def round(self) -> IntValue: ...

    @overload
    def round(self, ndigits: IntLike) -> FloatValue: ...

    def round(self, ndigits: IntLike | None = None) -> FloatValue | IntValue:
        if ndigits is None:
            from spellbind.int_values import IntValue
            round_to_int_fun: Callable[[float], int] = round
            return IntValue.derive_from_one(round_to_int_fun, self)
        round_fun: Callable[[float, int], float] = round
        return FloatValue.derive_from_two(round_fun, self, ndigits)

    def __lt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.lt)

    def __le__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.le)

    def __gt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.gt)

    def __ge__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.ge)

    def __neg__(self) -> FloatValue:
        return NegateFloatValue(self)

    def __pos__(self) -> Self:
        return self

    def clamp(self, min_value: FloatLike, max_value: FloatLike) -> FloatValue:
        return FloatValue.derive_from_three_floats(_clamp_float, self, min_value, max_value)

    def decompose_float_operands(self, operator_: Callable[[Sequence[float]], _S]) -> Sequence[FloatLike]:
        return (self,)

    @classmethod
    def derive_from_one(cls, transformer: Callable[[float], float], of: FloatLike) -> FloatValue:
        try:
            constant_value = _get_constant_float(of)
        except NotConstantError:
            return OneFloatToFloatValue(transformer, of)
        else:
            return FloatConstant.of(transformer(constant_value))

    @classmethod
    @overload
    def derive_from_two(cls, operator_: Callable[[float, int], float], first: FloatLike, second: IntLike) -> FloatValue: ...

    @classmethod
    @overload
    def derive_from_two(cls, operator_: Callable[[float, float], float], first: FloatLike, second: FloatLike) -> FloatValue: ...

    @classmethod
    def derive_from_two(cls, operator_, first, second) -> FloatValue:
        try:
            constant_first = _get_constant_float(first)
            constant_second = _get_constant_float(second)
        except NotConstantError:
            return TwoFloatsToFloatsValue(operator_, first, second)
        else:
            return FloatConstant.of(operator_(constant_first, constant_second))

    @classmethod
    def derive_from_three_floats(cls, transformer: Callable[[float, float, float], float],
                                 first: FloatLike, second: FloatLike, third: FloatLike) -> FloatValue:
        try:
            constant_first = _get_constant_float(first)
            constant_second = _get_constant_float(second)
            constant_third = _get_constant_float(third)
        except NotConstantError:
            return ThreeFloatToFloatValue(transformer, first, second, third)
        else:
            return FloatConstant.of(transformer(constant_first, constant_second, constant_third))

    @classmethod
    def derive_from_three(cls, transformer: Callable[[_S, _T, _U], float],
                          first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> FloatValue:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToFloatValue.create,
            create_constant=FloatConstant.of,
        )

    @classmethod
    def derive_from_many(cls, transformer: Callable[[Sequence[float]], float], *values: FloatLike, is_associative: bool = False) -> FloatValue:
        try:
            constant_values = [_get_constant_float(v) for v in values]
        except NotConstantError:
            if is_associative:
                flattened = [item for v in values for item in _decompose_float_operands(transformer, v)]
                return ManyFloatsToFloatValue(transformer, *flattened)
            else:
                return ManyFloatsToFloatValue(transformer, *values)
        else:
            return FloatConstant.of(transformer(constant_values))


def min_float(*values: FloatLike) -> FloatValue:
    return FloatValue.derive_from_many(min, *values, is_associative=True)


def max_float(*values: FloatLike) -> FloatValue:
    return FloatValue.derive_from_many(max, *values, is_associative=True)


def average_floats(*values: FloatLike) -> FloatValue:
    return FloatValue.derive_from_many(_average_float, *values)


def sum_floats(*values: FloatLike) -> FloatValue:
    return FloatValue.derive_from_many(sum, *values, is_associative=True)


def multiply_floats(*values: FloatLike) -> FloatValue:
    return FloatValue.derive_from_many(_multiply_all_floats, *values, is_associative=True)


class OneToFloatValue(Generic[_S], OneToOneValue[_S, float], FloatValue):
    pass


class FloatConstant(FloatValue, Constant[float]):
    _cache: dict[float, FloatConstant] = {}

    @classmethod
    def of(cls, value: float) -> FloatConstant:
        try:
            return FloatConstant._cache[value]
        except KeyError:
            return FloatConstant(value)

    def __abs__(self):
        if self.value >= 0:
            return self
        return FloatConstant.of(-self.value)

    def __neg__(self):
        return FloatConstant.of(-self.value)


for _value in [*range(101)]:
    FloatConstant._cache[_value] = FloatConstant(_value)
    FloatConstant._cache[-_value] = FloatConstant(-_value)


class FloatVariable(SimpleVariable[float], FloatValue):
    pass


def _create_float_getter(value: float | Value[int] | Value[float]) -> Callable[[], float]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


class OneFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float], _S], of: FloatLike):
        self._of = of
        self._getter = _create_float_getter(of)
        self._transformer = transformer
        super().__init__(*[v for v in (of,) if isinstance(v, Value)])

    @property
    def value(self) -> _S:
        return self._value

    def _calculate_value(self) -> _S:
        return self._transformer(self._getter())


class OneFloatToFloatValue(OneFloatToOneValue[float], FloatValue):
    pass


def _get_constant_float(value: FloatLike) -> float:
    if isinstance(value, Value):
        return value.constant_value_or_raise
    return value


def _decompose_float_operands(operator_: Callable, value: FloatLike) -> Sequence[FloatLike]:
    if isinstance(value, Value):
        if isinstance(value, FloatValue):
            return value.decompose_float_operands(operator_)
        return value.decompose_operands(operator_)
    return (value,)


class ManyFloatsToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[Sequence[float]], _S], *values: FloatLike):
        self._input_values = tuple(values)
        self._value_getters = [_create_float_getter(v) for v in self._input_values]
        self._transformer = transformer
        super().__init__(*[v for v in self._input_values if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        gotten_values = [getter() for getter in self._value_getters]
        return self._transformer(gotten_values)


class ManyFloatsToFloatValue(ManyFloatsToOneValue[float], FloatValue):
    def decompose_float_operands(self, operator_: Callable) -> Sequence[FloatLike]:
        if self._transformer == operator_:
            return self._input_values
        return (self,)


class TwoFloatsToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float, float], _S],
                 first: FloatLike, second: FloatLike):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._first_getter = _create_float_getter(first)
        self._second_getter = _create_float_getter(second)
        super().__init__(*[v for v in (first, second) if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        return self._transformer(self._first_getter(), self._second_getter())


class TwoFloatsToFloatsValue(TwoFloatsToOneValue[float], FloatValue):
    def decompose_float_operands(self, operator_: Callable) -> Sequence[FloatLike]:
        if self._transformer == operator_:
            return self._of_first, self._of_second
        return (self,)


class ThreeFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float, float, float], _S],
                 first: FloatLike, second: FloatLike, third: FloatLike):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._of_third = third
        self._first_getter = _create_float_getter(first)
        self._second_getter = _create_float_getter(second)
        self._third_getter = _create_float_getter(third)
        super().__init__(*[v for v in (first, second, third) if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        return self._transformer(self._first_getter(), self._second_getter(), self._third_getter())


class ThreeFloatToFloatValue(ThreeFloatToOneValue[float], FloatValue):
    def decompose_float_operands(self, operator_: Callable) -> Sequence[FloatLike]:
        if self._transformer == operator_:
            return self._of_first, self._of_second, self._of_third
        return (self,)


class ThreeToFloatValue(ThreeToOneValue[_S, _T, _U, float], FloatValue):
    @classmethod
    def create(cls, transformer: Callable[[_S, _T, _U], float],
               first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> FloatValue:
        return ThreeToFloatValue(transformer, first, second, third)


class AbsFloatValue(OneFloatToOneValue[float], FloatValue):
    def __init__(self, value: FloatLike):
        super().__init__(abs, value)

    def __abs__(self) -> Self:
        return self


class NegateFloatValue(OneFloatToFloatValue, FloatValue):
    def __init__(self, value: FloatLike):
        super().__init__(operator.neg, value)

    def __neg__(self) -> FloatValue:
        of = self._of
        if isinstance(of, FloatValue):
            return of
        return super().__neg__()


class CompareNumbersValues(TwoFloatsToOneValue[bool], BoolValue):
    def __init__(self, left: FloatLike, right: FloatLike, op: Callable[[float, float], bool]):
        super().__init__(op, left, right)
