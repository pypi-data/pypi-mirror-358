from conftest import OneParameterObserver
from spellbind.float_values import FloatVariable, FloatConstant
from spellbind.int_values import IntVariable


def test_floor_float_value():
    v0 = FloatVariable(3.7)
    v1 = v0.floor()
    assert v1.value == 3

    v0.value = -2.3
    assert v1.value == -3


def test_ceil_float_value():
    v0 = FloatVariable(3.2)
    v1 = v0.ceil()
    assert v1.value == 4

    v0.value = -2.8
    assert v1.value == -2


def test_round_float_value_no_digits():
    v0 = FloatVariable(3.7)
    v1 = v0.round()
    assert v1.value == 4

    v0.value = 2.3
    assert v1.value == 2


def test_round_float_value_with_digits():
    v0 = FloatVariable(3.14159)
    v1 = v0.round(2)
    assert v1.value == 3.14

    v0.value = 2.71828
    assert v1.value == 2.72


def test_round_float_value_with_int_value_digits():
    v0 = FloatVariable(3.14159)
    v1 = IntVariable(2)
    v2 = v0.round(v1)
    assert v2.value == 3.14

    v1.value = 3
    assert v2.value == 3.142


def test_round_float_change_comma_doesnt_change_int_value():
    v0 = FloatVariable(3.14159)
    rounded = v0.round()
    observer = OneParameterObserver()
    rounded.observe(observer)
    assert rounded.value == 3

    v0.value = 3.3
    assert rounded.value == 3

    observer.assert_not_called()


def test_round_constant_float_is_constant_value():
    v0 = FloatConstant(3.14159)
    v1 = v0.round(2)
    assert isinstance(v1, FloatConstant)
