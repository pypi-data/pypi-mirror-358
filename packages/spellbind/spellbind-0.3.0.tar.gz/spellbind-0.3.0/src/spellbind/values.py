from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any, Iterable, TYPE_CHECKING, Callable, Sequence

from spellbind.event import ValueEvent
from spellbind.observables import ValueObservable, Observer, ValueObserver

if TYPE_CHECKING:
    from spellbind.str_values import StrValue  # pragma: no cover
    from spellbind.int_values import IntValue  # pragma: no cover
    from spellbind.bool_values import BoolValue  # pragma: no cover
    from spellbind.float_values import FloatValue  # pragma: no cover


EMPTY_FROZEN_SET: frozenset = frozenset()

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_W = TypeVar("_W")


def _create_value_getter(value: Value[_S] | _S) -> Callable[[], _S]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


class NotConstantError(Exception):
    pass


class Value(ValueObservable[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def value(self) -> _S: ...

    @abstractmethod
    def derived_from(self) -> frozenset[Value]: ...

    @property
    def deep_derived_from(self) -> Iterable[Value]:
        found_derived = set()
        derive_queue = [self]

        while derive_queue:
            current = derive_queue.pop(0)
            for dependency in current.derived_from():
                if dependency not in found_derived:
                    found_derived.add(dependency)
                    yield dependency
                    derive_queue.append(dependency)

    def is_dependent_on(self, value: Value[Any]) -> bool:
        for dependency in self.deep_derived_from:
            if value is dependency:
                return True
        return False

    def to_str(self) -> StrValue:
        from spellbind.str_values import ToStrValue
        return ToStrValue(self)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def map(self, transformer: Callable[[_S], _T]) -> Value[_T]:
        return OneToOneValue(transformer, self)

    def map_to_int(self, transformer: Callable[[_S], int]) -> IntValue:
        from spellbind.int_values import OneToIntValue
        return OneToIntValue(transformer, self)

    def map_to_float(self, transformer: Callable[[_S], float]) -> FloatValue:
        from spellbind.float_values import OneToFloatValue
        return OneToFloatValue(transformer, self)

    def map_to_str(self, transformer: Callable[[_S], str]) -> StrValue:
        from spellbind.str_values import OneToStrValue
        return OneToStrValue(transformer, self)

    def map_to_bool(self, transformer: Callable[[_S], bool]) -> BoolValue:
        from spellbind.bool_values import OneToBoolValue
        return OneToBoolValue(transformer, self)

    @property
    def constant_value_or_raise(self) -> _S:
        raise NotConstantError

    def decompose_operands(self, operator_: Callable) -> Sequence[Value[_S] | _S]:
        return (self,)

    @classmethod
    def derive_from_two_with_factory(
            cls,
            transformer: Callable[[_S, _T], _U],
            first: _S | Value[_S], second: _T | Value[_T],
            create_value: Callable[[Callable[[_S, _T], _U], _S | Value[_S], _T | Value[_T]], _V],
            create_constant: Callable[[_U], _V]) -> _V:
        try:
            constant_first = get_constant_of_generic_like(first)
            constant_second = get_constant_of_generic_like(second)
        except NotConstantError:
            return create_value(transformer, first, second)
        else:
            return create_constant(transformer(constant_first, constant_second))

    @classmethod
    def derive_from_three_with_factory(
            cls,
            transformer: Callable[[_S, _T, _U], _V],
            first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U],
            create_value: Callable[[Callable[[_S, _T, _U], _V], _S | Value[_S], _T | Value[_T], _U | Value[_U]], _W],
            create_constant: Callable[[_V], _W]) -> _W:
        try:
            constant_first = get_constant_of_generic_like(first)
            constant_second = get_constant_of_generic_like(second)
            constant_third = get_constant_of_generic_like(third)
        except NotConstantError:
            return create_value(transformer, first, second, third)
        else:
            return create_constant(transformer(constant_first, constant_second, constant_third))

    @classmethod
    def derive_three_value(
            cls,
            transformer: Callable[[_S, _T, _U], _V],
            first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> Value[_V]:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToOneValue.create,
            create_constant=Constant.of
        )

    @classmethod
    def derive_from_many_with_factory(
            cls,
            transformer: Callable[[Iterable[_S]], _S], *values: _S | Value[_S],
            create_value: Callable[[Callable[[Iterable[_S]], _S], Sequence[_S | Value[_S]]], _T],
            create_constant: Callable[[_S], _T],
            is_associative: bool = False) -> _T:
        try:
            constant_values = [get_constant_of_generic_like(v) for v in values]
        except NotConstantError:
            if is_associative:
                flattened = tuple(item for v in values for item in decompose_operands_of_generic_like(transformer, v))
                return create_value(transformer, flattened)
            else:
                return create_value(transformer, values)
        else:
            return create_constant(transformer(constant_values))


class Variable(Value[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def value(self) -> _S: ...

    @value.setter
    @abstractmethod
    def value(self, new_value: _S) -> None: ...

    @abstractmethod
    def bind_to(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None: ...

    @abstractmethod
    def unbind(self, not_bound_ok: bool = False) -> None: ...


class SimpleVariable(Variable[_S], Generic[_S]):
    _bound_to_set: frozenset[Value[_S]]
    _on_change: ValueEvent[_S]
    _bound_to: Optional[Value[_S]]

    def __init__(self, value: _S):
        self._bound_to_set = EMPTY_FROZEN_SET
        self._value = value
        self._on_change = ValueEvent()
        self._bound_to = None

    @property
    def value(self) -> _S:
        return self._value

    @value.setter
    def value(self, new_value: _S) -> None:
        if self._bound_to is not None:
            raise ValueError("Cannot set value of a Variable that is bound to a Value.")
        self._set_value_bypass_bound_check(new_value)

    def _set_value_bypass_bound_check(self, new_value: _S) -> None:
        if new_value != self._value:
            self._value = new_value
            self._on_change(new_value)

    def _receive_bound_value(self, value: _S) -> None:
        self._set_value_bypass_bound_check(value)

    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.observe(observer, times)

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.weak_observe(observer, times)

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        self._on_change.unobserve(observer)

    def bind_to(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None:
        if value is self:
            raise RecursionError("Cannot bind a Variable to itself.")
        if value.is_dependent_on(self):
            raise RecursionError("Circular binding detected.")
        if self._bound_to is not None:
            if not already_bound_ok:
                raise ValueError("Variable is already bound to another Value.")
            if self._bound_to is value:
                return
            self.unbind()
        if bind_weakly:
            value.weak_observe(self._receive_bound_value)
        else:
            value.observe(self._receive_bound_value)
        self._bound_to = value
        self._bound_to_set = frozenset([value])
        self._set_value_bypass_bound_check(value.value)

    def unbind(self, not_bound_ok: bool = False) -> None:
        if self._bound_to is None:
            if not not_bound_ok:
                raise ValueError("Variable is not bound to any Value.")
            else:
                return

        self._bound_to.unobserve(self._receive_bound_value)
        self._bound_to = None
        self._bound_to_set = EMPTY_FROZEN_SET

    def derived_from(self) -> frozenset[Value[_S]]:
        return self._bound_to_set


class Constant(Value[_S], Generic[_S]):
    _value: _S

    def __init__(self, value: _S):
        self._value = value

    @property
    def value(self) -> _S:
        return self._value

    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        pass

    def derived_from(self) -> frozenset[Value[_S]]:
        return EMPTY_FROZEN_SET

    @property
    def constant_value_or_raise(self) -> _S:
        return self._value

    @classmethod
    def of(cls, value: _S) -> Constant[_S]:
        return Constant(value)


class DerivedValueBase(Value[_S], Generic[_S], ABC):
    def __init__(self, *derived_from: Value):
        self._derived_from = frozenset(derived_from)
        self._on_change: ValueEvent[_S] = ValueEvent()
        for value in derived_from:
            value.weak_observe(self._on_dependency_changed)
        self._value = self._calculate_value()

    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.observe(observer, times)

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.weak_observe(observer, times)

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        self._on_change.unobserve(observer)

    def derived_from(self) -> frozenset[Value]:
        return self._derived_from

    def _on_dependency_changed(self) -> None:
        new_value = self._calculate_value()
        if new_value != self._value:
            self._value = new_value
            self._on_change(self._value)

    @abstractmethod
    def _calculate_value(self) -> _S: ...

    @property
    def value(self) -> _S:
        return self._value


class OneToOneValue(DerivedValueBase[_T], Generic[_S, _T]):
    _getter: Callable[[], _S]

    def __init__(self, transformer: Callable[[_S], _T], of: Value[_S]):
        self._getter = _create_value_getter(of)
        self._of = of
        self._transformer = transformer
        super().__init__(*[v for v in (of,) if isinstance(v, Value)])

    def _calculate_value(self) -> _T:
        return self._transformer(self._getter())


class ManyToOneValue(DerivedValueBase[_T], Generic[_S, _T]):
    def __init__(self, transformer: Callable[[Iterable[_S]], _T], *values: _S | Value[_S]):
        self._input_values = tuple(values)
        self._value_getters = [_create_value_getter(v) for v in self._input_values]
        self._transformer = transformer
        super().__init__(*[v for v in self._input_values if isinstance(v, Value)])

    def _calculate_value(self) -> _T:
        gotten_values = [getter() for getter in self._value_getters]
        return self._transformer(gotten_values)


class ManyToSameValue(ManyToOneValue[_S, _S], Generic[_S]):
    def decompose_operands(self, transformer: Callable) -> Sequence[Value[_S] | _S]:
        if transformer == self._transformer:
            return self._input_values
        return (self,)


class TwoToOneValue(DerivedValueBase[_U], Generic[_S, _T, _U]):
    def __init__(self, transformer: Callable[[_S, _T], _U],
                 first: Value[_S] | _S, second: Value[_T] | _T):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._first_getter = _create_value_getter(first)
        self._second_getter = _create_value_getter(second)
        super().__init__(*[v for v in (first, second) if isinstance(v, Value)])

    def _calculate_value(self) -> _U:
        return self._transformer(self._first_getter(), self._second_getter())


class ThreeToOneValue(DerivedValueBase[_V], Generic[_S, _T, _U, _V]):
    def __init__(self, transformer: Callable[[_S, _T, _U], _V],
                 first: Value[_S] | _S, second: Value[_T] | _T, third: Value[_U] | _U):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._of_third = third
        self._first_getter = _create_value_getter(first)
        self._second_getter = _create_value_getter(second)
        self._third_getter = _create_value_getter(third)
        super().__init__(*[v for v in (first, second, third) if isinstance(v, Value)])

    def _calculate_value(self) -> _V:
        return self._transformer(self._first_getter(), self._second_getter(), self._third_getter())

    @classmethod
    def create(cls, transformer: Callable[[_S, _T, _U], _V],
               first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> Value[_V]:
        return ThreeToOneValue(transformer, first, second, third)


def get_constant_of_generic_like(value: _S | Value[_S]) -> _S:
    if isinstance(value, Value):
        return value.constant_value_or_raise
    return value


def decompose_operands_of_generic_like(operator_: Callable, value: _S | Value[_S]) -> Sequence[_S | Value[_S]]:
    if isinstance(value, Value):
        return value.decompose_operands(operator_)
    return (value,)
