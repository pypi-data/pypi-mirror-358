from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic

from spellbind.emitters import Emitter, TriEmitter, BiEmitter, ValueEmitter
from spellbind.functions import assert_parameter_max_count
from spellbind.observables import Observable, ValueObservable, BiObservable, TriObservable, Observer, \
    ValueObserver, BiObserver, TriObserver, Subscription, WeakSubscription, StrongSubscription, \
    RemoveSubscriptionError

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_O = TypeVar('_O', bound=Callable)


class _BaseEvent(Generic[_O], ABC):
    _subscriptions: list[Subscription[_O]]

    def __init__(self):
        self._subscriptions = []

    @abstractmethod
    def _get_parameter_count(self) -> int: ...

    def observe(self, observer: _O, times: int | None = None) -> None:
        assert_parameter_max_count(observer, self._get_parameter_count())
        self._subscriptions.append(StrongSubscription(observer, times))

    def weak_observe(self, observer: _O, times: int | None = None) -> None:
        assert_parameter_max_count(observer, self._get_parameter_count())
        self._subscriptions.append(WeakSubscription(observer, times))

    def unobserve(self, observer: _O) -> None:
        for i, sub in enumerate(self._subscriptions):
            if sub.matches_observer(observer):
                del self._subscriptions[i]
                return
        raise ValueError(f"Observer {observer} is not subscribed to this event.")

    def is_observed(self, observer: _O) -> bool:
        return any(sub.matches_observer(observer) for sub in self._subscriptions)

    def _emit(self, *args) -> None:
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i](*args)
                i += 1
            except RemoveSubscriptionError:
                del self._subscriptions[i]


class Event(_BaseEvent[Observer], Observable, Emitter):
    def _get_parameter_count(self) -> int:
        return 0

    def __call__(self) -> None:
        self._emit()


class ValueEvent(Generic[_S], _BaseEvent[Observer | ValueObserver[_S]], ValueObservable[_S], ValueEmitter[_S]):
    def _get_parameter_count(self) -> int:
        return 1

    def __call__(self, value: _S) -> None:
        self._emit(value)


class BiEvent(Generic[_S, _T], _BaseEvent[Observer | ValueObserver[_S] | BiObserver[_S, _T]], BiObservable[_S, _T], BiEmitter[_S, _T]):
    def _get_parameter_count(self) -> int:
        return 2

    def __call__(self, value_0: _S, value_1: _T) -> None:
        self._emit(value_0, value_1)


class TriEvent(Generic[_S, _T, _U], _BaseEvent[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]], TriObservable[_S, _T, _U], TriEmitter[_S, _T, _U]):
    def _get_parameter_count(self) -> int:
        return 3

    def __call__(self, value_0: _S, value_1: _T, value_2: _U) -> None:
        self._emit(value_0, value_1, value_2)
