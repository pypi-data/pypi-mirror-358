import pytest

from spellbind.str_values import StrConstant, StrVariable


def test_str_constant_str():
    const = StrConstant("hello")
    assert str(const) == "hello"


def test_str_length_of_variable():
    v0 = StrVariable("foo")
    v0_length = v0.length
    assert v0_length.value == 3
    v0.value = "foobar"
    assert v0_length.value == 6


def test_str_length_of_constant():
    const = StrConstant("hello")
    const_length = const.length
    assert const_length.constant_value_or_raise == 5


@pytest.mark.parametrize("value", ["a", "A", "0", "!"])
def test_str_constant_is_same(value: str):
    v0 = StrConstant.of(value)
    v1 = StrConstant.of(value)
    assert v0 is v1
