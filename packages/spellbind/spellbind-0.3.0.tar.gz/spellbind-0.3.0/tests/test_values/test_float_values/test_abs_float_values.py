from spellbind.float_values import FloatVariable, FloatConstant


def test_abs_float_value_positive():
    v0 = FloatVariable(5.5)
    v1 = abs(v0)
    assert v1.value == 5.5

    v0.value = 10.8
    assert v1.value == 10.8


def test_abs_float_value_negative():
    v0 = FloatVariable(-5.5)
    v1 = abs(v0)
    assert v1.value == 5.5

    v0.value = -10.8
    assert v1.value == 10.8


def test_abs_float_value_zero():
    v0 = FloatVariable(0.0)
    v1 = abs(v0)
    assert v1.value == 0.0

    v0.value = -7.2
    assert v1.value == 7.2


def test_abs_of_abs_value_is_itself():
    v0 = FloatVariable(-5.5)
    v1 = abs(v0)
    v2 = abs(v1)
    assert v2 is v1


def test_abs_of_constant_is_constant():
    v0 = FloatConstant(-5.5)
    v1 = abs(v0)
    assert v1.value == 5.5
    assert isinstance(v1, FloatConstant)


def test_abs_of_positive_constant_is_itself():
    v0 = FloatConstant(5.5)
    v1 = abs(v0)
    assert v1 is v0
    assert v1.value == 5.5
