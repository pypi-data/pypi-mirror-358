from spellbind.float_values import FloatVariable, FloatConstant
from spellbind.int_values import IntVariable


def test_truediv_float_value_by_float():
    v0 = FloatVariable(10.0)
    v2 = v0 / 4.0
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_value_by_int():
    v0 = FloatVariable(10.0)
    v2 = v0 / 4
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_value_by_int_value():
    v0 = FloatVariable(10.0)
    v1 = IntVariable(4)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_divided_by_float_value():
    v1 = FloatVariable(4.0)
    v2 = 10.0 / v1
    assert v2.value == 2.5

    v1.value = 5.0
    assert v2.value == 2.0


def test_truediv_int_divided_by_float_value():
    v1 = FloatVariable(4.0)
    v2 = 10 / v1
    assert v2.value == 2.5

    v1.value = 5.0
    assert v2.value == 2.0


def test_truediv_float_values():
    v0 = FloatVariable(10.0)
    v1 = FloatVariable(4.0)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_constant_constant_is_constant():
    v0 = FloatConstant(10.0)
    v1 = FloatConstant(4.0)
    v2 = v0 / v1
    assert v2.value == 2.5
    assert isinstance(v2, FloatConstant)


def test_truediv_literal_constant_is_constant():
    v0 = FloatConstant(10.0)
    v2 = v0 / 4.0
    assert v2.value == 2.5
    assert isinstance(v2, FloatConstant)


def test_truediv_constant_literal_is_constant():
    v0 = FloatConstant(4.0)
    v2 = 10.0 / v0
    assert v2.value == 2.5
    assert isinstance(v2, FloatConstant)
