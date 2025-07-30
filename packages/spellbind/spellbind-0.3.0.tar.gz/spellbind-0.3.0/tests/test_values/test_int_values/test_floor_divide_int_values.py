from spellbind.int_values import IntVariable, IntConstant


def test_floordiv_int_values():
    v0 = IntVariable(10)
    v1 = IntVariable(3)
    v2 = v0 // v1
    assert v2.value == 3

    v0.value = 15
    assert v2.value == 5


def test_floordiv_int_value_by_int():
    v0 = IntVariable(10)
    v2 = v0 // 3
    assert v2.value == 3

    v0.value = 15
    assert v2.value == 5


def test_floordiv_int_divided_by_int_value():
    v1 = IntVariable(3)
    v2 = 10 // v1
    assert v2.value == 3

    v1.value = 4
    assert v2.value == 2


def test_floordiv_constant_constant_is_constant():
    v0 = IntConstant(10)
    v1 = IntConstant(3)
    v2 = v0 // v1
    assert v2.value == 3
    assert isinstance(v2, IntConstant)


def test_floordiv_literal_constant_is_constant():
    v0 = IntConstant(10)
    v2 = v0 // 3
    assert v2.value == 3
    assert isinstance(v2, IntConstant)


def test_floordiv_constant_literal_is_constant():
    v0 = IntConstant(3)
    v2 = 10 // v0
    assert v2.value == 3
    assert isinstance(v2, IntConstant)
