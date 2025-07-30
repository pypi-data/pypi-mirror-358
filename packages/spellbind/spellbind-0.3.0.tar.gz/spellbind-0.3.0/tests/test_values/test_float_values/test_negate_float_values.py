from spellbind.float_values import FloatVariable, FloatConstant


def test_negate_float_value():
    v0 = FloatVariable(5.5)
    v1 = -v0
    assert v1.value == -5.5

    v0.value = -3.2
    assert v1.value == 3.2


def test_negate_float_value_zero():
    v0 = FloatVariable(0.0)
    v1 = -v0
    assert v1.value == 0.0

    v0.value = 7.8
    assert v1.value == -7.8


def test_negate_float_constant_is_constant():
    v0 = FloatConstant(5.5)
    v1 = -v0
    assert v1.value == -5.5

    assert isinstance(v0, FloatConstant)


def test_negate_variable_twice_is_same():
    v0 = FloatVariable(5.5)
    v1 = -v0
    v2 = -v1
    assert v0 is v2
