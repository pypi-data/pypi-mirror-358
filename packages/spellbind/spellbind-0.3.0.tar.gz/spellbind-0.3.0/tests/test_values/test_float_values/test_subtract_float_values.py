from spellbind.float_values import FloatVariable, FloatConstant
from spellbind.int_values import IntVariable


def test_subtract_float_values():
    v0 = FloatVariable(5.5)
    v1 = FloatVariable(2.5)
    v2 = v0 - v1
    assert v2.value == 3.0

    v0.value = 10.5
    assert v2.value == 8.0


def test_subtract_float_value_minus_float():
    v0 = FloatVariable(5.5)
    v2 = v0 - 2.5
    assert v2.value == 3.0

    v0.value = 10.5
    assert v2.value == 8.0


def test_subtract_float_value_minus_int():
    v0 = FloatVariable(5.5)
    v2 = v0 - 2
    assert v2.value == 3.5

    v0.value = 10.5
    assert v2.value == 8.5


def test_subtract_float_value_minus_int_value():
    v0 = FloatVariable(5.5)
    v1 = IntVariable(2)
    v2 = v0 - v1
    assert v2.value == 3.5

    v0.value = 10.5
    assert v2.value == 8.5


def test_subtract_float_minus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 5.5 - v1
    assert v2.value == 3.0

    v1.value = 1.5
    assert v2.value == 4.0


def test_subtract_int_minus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 5 - v1
    assert v2.value == 2.5

    v1.value = 1.5
    assert v2.value == 3.5


def test_subtract_constant_from_constant_is_constant():
    v0 = FloatConstant(5.5)
    v1 = FloatConstant(2.5)
    v2 = v0 - v1
    assert v2.value == 3.0
    assert isinstance(v2, FloatConstant)


def test_subtract_literal_from_constant_is_constant():
    v0 = FloatConstant(5.5)
    v2 = v0 - 2.5
    assert v2.value == 3.0
    assert isinstance(v2, FloatConstant)


def test_subtract_constant_from_literal_is_constant():
    v0 = FloatConstant(5.5)
    v2 = 8.0 - v0
    assert v2.value == 2.5
    assert isinstance(v2, FloatConstant)


def test_subtract_twice():
    v0 = FloatVariable(5.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(1.0)

    v3 = (v0 - v1) - v2
    assert v3.value == 2.0
