from __future__ import annotations

import operator
from abc import ABC
from typing import overload, Generic, Callable, Iterable

from typing_extensions import Self, TypeVar

from spellbind.bool_values import BoolValue
from spellbind.float_values import FloatValue, \
    CompareNumbersValues
from spellbind.functions import _clamp_int, _multiply_all_ints, _multiply_all_floats
from spellbind.values import Value, SimpleVariable, TwoToOneValue, OneToOneValue, Constant, \
    ThreeToOneValue, NotConstantError, ManyToSameValue, get_constant_of_generic_like

IntLike = int | Value[int]
FloatLike = IntLike | float | FloatValue


_S = TypeVar('_S')
_T = TypeVar('_T')
_U = TypeVar('_U')


class IntValue(Value[int], ABC):
    @overload
    def __add__(self, other: IntLike) -> IntValue: ...

    @overload
    def __add__(self, other: float | FloatValue) -> FloatValue: ...

    def __add__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return FloatValue.derive_from_many(sum, self, other, is_associative=True)
        return IntValue.derive_from_many(sum, self, other, is_associative=True)

    @overload
    def __radd__(self, other: int) -> IntValue: ...

    @overload
    def __radd__(self, other: float) -> FloatValue: ...

    def __radd__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return FloatValue.derive_from_many(sum, other, self, is_associative=True)
        return IntValue.derive_from_many(sum, other, self, is_associative=True)

    @overload
    def __sub__(self, other: IntLike) -> IntValue: ...

    @overload
    def __sub__(self, other: float | FloatValue) -> FloatValue: ...

    def __sub__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return FloatValue.derive_from_two(operator.sub, self, other)
        return IntValue.derive_from_two(operator.sub, self, other)

    @overload
    def __rsub__(self, other: int) -> IntValue: ...

    @overload
    def __rsub__(self, other: float) -> FloatValue: ...

    def __rsub__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return FloatValue.derive_from_two(operator.sub, other, self)
        return IntValue.derive_from_two(operator.sub, other, self)

    @overload
    def __mul__(self, other: IntLike) -> IntValue: ...

    @overload
    def __mul__(self, other: float | FloatValue) -> FloatValue: ...

    def __mul__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return FloatValue.derive_from_many(_multiply_all_floats, self, other, is_associative=True)
        return IntValue.derive_from_many(_multiply_all_ints, self, other, is_associative=True)

    @overload
    def __rmul__(self, other: int) -> IntValue: ...

    @overload
    def __rmul__(self, other: float) -> FloatValue: ...

    def __rmul__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return FloatValue.derive_from_many(_multiply_all_floats, other, self, is_associative=True)
        return IntValue.derive_from_many(_multiply_all_ints, other, self, is_associative=True)

    def __truediv__(self, other: FloatLike) -> FloatValue:
        return FloatValue.derive_from_two(operator.truediv, self, other)

    def __rtruediv__(self, other: int | float) -> FloatValue:
        return FloatValue.derive_from_two(operator.truediv, other, self)

    def __floordiv__(self, other: IntLike) -> IntValue:
        return IntValue.derive_from_two(operator.floordiv, self, other)

    def __rfloordiv__(self, other: int) -> IntValue:
        return IntValue.derive_from_two(operator.floordiv, other, self)

    def __pow__(self, other: IntLike) -> IntValue:
        return IntValue.derive_from_two(operator.pow, self, other)

    def __rpow__(self, other: int) -> IntValue:
        return IntValue.derive_from_two(operator.pow, other, self)

    def __mod__(self, other: IntLike) -> IntValue:
        return IntValue.derive_from_two(operator.mod, self, other)

    def __rmod__(self, other: int) -> IntValue:
        return IntValue.derive_from_two(operator.mod, other, self)

    def __abs__(self) -> IntValue:
        return AbsIntValue(self)

    def __lt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.lt)

    def __le__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.le)

    def __gt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.gt)

    def __ge__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.ge)

    def __neg__(self) -> IntValue:
        return NegateIntValue(self)

    def __pos__(self) -> Self:
        return self

    def clamp(self, min_value: IntLike, max_value: IntLike) -> IntValue:
        return IntValue.derive_from_three(_clamp_int, self, min_value, max_value)

    @classmethod
    def derive_from_one(cls, operator_: Callable[[_S], int], value: _S | Value[_S]) -> IntValue:
        if not isinstance(value, Value):
            return IntConstant.of(operator_(value))
        try:
            constant_value = value.constant_value_or_raise
        except NotConstantError:
            return OneToIntValue(operator_, value)
        else:
            return IntConstant.of(operator_(constant_value))

    @classmethod
    def derive_from_two(cls, operator_: Callable[[int, int], int], left: IntLike, right: IntLike) -> IntValue:
        try:
            left_value = get_constant_of_generic_like(left)
            right_value = get_constant_of_generic_like(right)
        except NotConstantError:
            return TwoToIntValue(operator_, left, right)
        else:
            return IntConstant.of(operator_(left_value, right_value))

    @classmethod
    def derive_from_three(cls, transformer: Callable[[_S, _T, _U], int],
                          first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> IntValue:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToIntValue.create,
            create_constant=IntConstant.of,
        )

    @classmethod
    def derive_from_many(cls, transformer: Callable[[Iterable[int]], int], *values: IntLike, is_associative: bool = False) -> IntValue:
        return Value.derive_from_many_with_factory(
            transformer,
            *values,
            create_value=ManyIntsToIntValue.create,
            create_constant=IntConstant.of,
            is_associative=is_associative,
        )


def min_int(*values: IntLike) -> IntValue:
    return IntValue.derive_from_many(min, *values, is_associative=True)


def max_int(*values: IntLike) -> IntValue:
    return IntValue.derive_from_many(max, *values, is_associative=True)


class OneToIntValue(Generic[_S], OneToOneValue[_S, int], IntValue):
    pass


class TwoToIntValue(Generic[_S, _T], TwoToOneValue[_S, _T, int], IntValue):
    pass


class ThreeToIntValue(Generic[_S, _T, _U], ThreeToOneValue[_S, _T, _U, int], IntValue):
    @staticmethod
    def create(transformer: Callable[[_S, _T, _U], int], first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> IntValue:
        return ThreeToIntValue(transformer, first, second, third)


class IntConstant(IntValue, Constant[int]):
    _cache: dict[int, IntConstant] = {}

    @classmethod
    def of(cls, value: int) -> IntConstant:
        try:
            return cls._cache[value]
        except KeyError:
            return IntConstant(value)

    def __abs__(self):
        if self.value >= 0:
            return self
        return IntConstant.of(-self.value)

    def __neg__(self):
        return IntConstant.of(-self.value)


for _value in [*range(101)]:
    IntConstant._cache[_value] = IntConstant(_value)
    IntConstant._cache[-_value] = IntConstant(-_value)


class IntVariable(SimpleVariable[int], IntValue):
    pass


class ManyIntsToIntValue(ManyToSameValue[int], IntValue):
    @staticmethod
    def create(transformer: Callable[[Iterable[int]], int], values: Iterable[IntLike]) -> IntValue:
        return ManyIntsToIntValue(transformer, *values)


class AbsIntValue(OneToOneValue[int, int], IntValue):
    def __init__(self, value: Value[int]):
        super().__init__(abs, value)

    def __abs__(self) -> Self:
        return self


class NegateIntValue(OneToOneValue[int, int], IntValue):
    def __init__(self, value: Value[int]):
        super().__init__(operator.neg, value)

    def __neg__(self) -> IntValue:
        of = self._of
        if isinstance(of, IntValue):
            return of
        return super().__neg__()
