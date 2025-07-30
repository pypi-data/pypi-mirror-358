from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol
from weakref import WeakMethod, ref

from spellbind.functions import count_positional_parameters

_SC = TypeVar("_SC", contravariant=True)
_TC = TypeVar("_TC", contravariant=True)
_UC = TypeVar("_UC", contravariant=True)

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")

_O = TypeVar('_O', bound=Callable)


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_SC]):
    def __call__(self, arg: _SC, /) -> None: ...


class BiObserver(Protocol[_SC, _TC]):
    def __call__(self, arg1: _SC, arg2: _TC, /) -> None: ...


class TriObserver(Protocol[_SC, _TC, _UC]):
    def __call__(self, arg1: _SC, arg2: _TC, arg3: _UC, /) -> None: ...


class RemoveSubscriptionError(Exception):
    pass


class CallCountExceededError(RemoveSubscriptionError):
    pass


class DeadReferenceError(RemoveSubscriptionError):
    pass


class Subscription(Generic[_O], ABC):
    def __init__(self, observer: _O, times: int | None):
        self._positional_parameter_count = count_positional_parameters(observer)
        self.called_counter = 0
        self.max_call_count = times

    def _call(self, observer: _O, *args) -> None:
        self.called_counter += 1
        trimmed_args = args[:self._positional_parameter_count]
        observer(*trimmed_args)
        if self.max_call_count is not None and self.called_counter >= self.max_call_count:
            raise CallCountExceededError

    @abstractmethod
    def __call__(self, *args) -> None: ...

    @abstractmethod
    def matches_observer(self, observer: _O) -> bool: ...


class StrongSubscription(Subscription[_O], Generic[_O]):
    def __init__(self, observer: _O, times: int | None):
        super().__init__(observer, times)
        self._observer = observer

    def __call__(self, *args) -> None:
        self._call(self._observer, *args)

    def matches_observer(self, observer: _O) -> bool:
        return self._observer == observer


class WeakSubscription(Subscription[_O], Generic[_O]):
    _ref: ref[_O] | WeakMethod

    def __init__(self, observer: _O, times: int | None):
        super().__init__(observer, times)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    def __call__(self, *args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        self._call(observer, *args)

    def matches_observer(self, observer: _O) -> bool:
        return self._ref() == observer


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer, times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer, times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer) -> None: ...


class ValueObservable(Observable, Generic[_S], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None: ...


class BiObservable(ValueObservable[_S], Generic[_S, _T], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                     times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None: ...


class TriObservable(BiObservable[_S, _T], Generic[_S, _T, _U], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                     times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None: ...
