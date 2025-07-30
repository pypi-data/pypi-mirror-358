from spellbind.int_values import IntVariable, IntConstant


def test_modulo_int_values():
    v0 = IntVariable(10)
    v1 = IntVariable(3)
    v2 = v0 % v1
    assert v2.value == 1

    v0.value = 15
    assert v2.value == 0


def test_modulo_int_value_by_int():
    v0 = IntVariable(10)
    v2 = v0 % 3
    assert v2.value == 1

    v0.value = 15
    assert v2.value == 0


def test_modulo_int_by_int_value():
    v1 = IntVariable(3)
    v2 = 10 % v1
    assert v2.value == 1

    v1.value = 4
    assert v2.value == 2


def test_modulo_constant_constant_is_constant():
    v0 = IntConstant(10)
    v1 = IntConstant(3)
    v2 = v0 % v1
    assert v2.value == 1
    assert isinstance(v2, IntConstant)


def test_modulo_constant_literal_is_constant():
    v0 = IntConstant(10)
    v2 = v0 % 3
    assert v2.value == 1
    assert isinstance(v2, IntConstant)


def test_modulo_literal_const_is_constant():
    v0 = 10
    v1 = IntConstant(3)
    v2 = v0 % v1
    assert v2.value == 1
    assert isinstance(v2, IntConstant)
