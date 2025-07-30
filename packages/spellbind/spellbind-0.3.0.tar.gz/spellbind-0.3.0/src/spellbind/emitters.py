from abc import ABC, abstractmethod
from typing import TypeVar, Generic


T = TypeVar("T")
U = TypeVar("U")
S = TypeVar("S")


class Emitter(ABC):
    @abstractmethod
    def __call__(self) -> None: ...


class ValueEmitter(Generic[T], ABC):
    @abstractmethod
    def __call__(self, value0: T) -> None: ...


class BiEmitter(Generic[T, U], ABC):
    @abstractmethod
    def __call__(self, value0: T, value1: U) -> None: ...


class TriEmitter(Generic[T, U, S], ABC):
    @abstractmethod
    def __call__(self, value0: T, value1: U, value2: S) -> None: ...
