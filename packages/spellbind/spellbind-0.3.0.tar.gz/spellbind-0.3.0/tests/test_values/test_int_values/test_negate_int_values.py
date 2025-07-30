from spellbind.int_values import IntVariable, IntConstant


def test_negate_int_value():
    v0 = IntVariable(5)
    v1 = -v0
    assert v1.value == -5

    v0.value = -3
    assert v1.value == 3


def test_negate_int_value_zero():
    v0 = IntVariable(0)
    v1 = -v0
    assert v1.value == 0

    v0.value = 7
    assert v1.value == -7


def test_negate_int_constant_is_constant():
    v0 = IntConstant(5)
    v1 = -v0
    assert v1.value == -5

    assert isinstance(v0, IntConstant)


def test_negate_variable_twice_is_same():
    v0 = IntVariable(5)
    v1 = -v0
    v2 = -v1
    assert v0 is v2
