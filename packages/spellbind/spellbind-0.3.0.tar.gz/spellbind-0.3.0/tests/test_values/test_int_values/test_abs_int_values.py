from spellbind.int_values import IntVariable, IntConstant


def test_abs_int_value_positive():
    v0 = IntVariable(5)
    v1 = abs(v0)
    assert v1.value == 5

    v0.value = 10
    assert v1.value == 10


def test_abs_int_value_negative():
    v0 = IntVariable(-5)
    v1 = abs(v0)
    assert v1.value == 5

    v0.value = -10
    assert v1.value == 10


def test_abs_int_value_zero():
    v0 = IntVariable(0)
    v1 = abs(v0)
    assert v1.value == 0

    v0.value = -7
    assert v1.value == 7


def test_abs_of_abs_value_is_itself():
    v0 = IntVariable(-5)
    v1 = abs(v0)
    v2 = abs(v1)
    assert v2 is v1


def test_abs_of_constant_is_constant():
    v0 = IntConstant(-5)
    v1 = abs(v0)
    assert v1.value == 5
    assert isinstance(v1, IntConstant)


def test_abs_of_positive_constant_is_itself():
    v0 = IntConstant(5)
    v1 = abs(v0)
    assert v1 is v0
    assert v1.value == 5
