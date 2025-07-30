import pytest
from spellbind.values import Constant
from conftest import OneParameterObserver


def test_constant_constructor():
    constant = Constant("test_value")
    assert constant.value == "test_value"


def test_constant_constructor_complex_object():
    test_dict = {"key": "value", "number": 123}
    constant = Constant(test_dict)
    assert constant.value is test_dict


def test_constant_value_immutable():
    constant = Constant("original")

    with pytest.raises(AttributeError):
        constant.value = "changed"


def test_constant_observe_does_nothing():
    constant = Constant("test")
    observer = OneParameterObserver()

    constant.observe(observer)

    observer.assert_not_called()


def test_constant_unobserve_does_nothing():
    constant = Constant("test")
    observer = OneParameterObserver()

    constant.unobserve(observer)

    observer.assert_not_called()


def test_constant_derived_from_empty():
    constant = Constant("test")

    assert constant.derived_from() == frozenset()


def test_constant_deep_derived_from_empty():
    constant = Constant("test")

    assert list(constant.deep_derived_from) == []
