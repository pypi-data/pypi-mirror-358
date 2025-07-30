from spellbind.float_values import FloatVariable, FloatConstant
from spellbind.int_values import IntVariable


def test_modulo_float_values():
    v0 = FloatVariable(10.5)
    v1 = FloatVariable(3.0)
    v2 = v0 % v1
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_float():
    v0 = FloatVariable(10.5)
    v2 = v0 % 3.0
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_int():
    v0 = FloatVariable(10.5)
    v2 = v0 % 3
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_int_value():
    v0 = FloatVariable(10.5)
    v1 = IntVariable(3)
    v2 = v0 % v1
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_by_float_value():
    v1 = FloatVariable(3.0)
    v2 = 10.5 % v1
    assert v2.value == 1.5

    v1.value = 4.0
    assert v2.value == 2.5


def test_modulo_int_by_float_value():
    v1 = FloatVariable(3.0)
    v2 = 10 % v1
    assert v2.value == 1.0

    v1.value = 4.0
    assert v2.value == 2.0


def test_modulo_constant_constant_is_constant():
    v0 = FloatConstant(10.5)
    v1 = FloatConstant(3.0)
    v2 = v0 % v1
    assert v2.value == 1.5
    assert isinstance(v2, FloatConstant)


def test_modulo_constant_literal_is_constant():
    v0 = FloatConstant(10.5)
    v2 = v0 % 3.0
    assert v2.value == 1.5
    assert isinstance(v2, FloatConstant)


def test_modulo_literal_const_is_constant():
    v0 = 10.5
    v1 = FloatConstant(3.0)
    v2 = v0 % v1
    assert v2.value == 1.5
    assert isinstance(v2, FloatConstant)
