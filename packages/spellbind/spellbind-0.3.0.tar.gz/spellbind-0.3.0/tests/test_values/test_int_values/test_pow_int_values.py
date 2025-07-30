from spellbind.int_values import IntVariable, IntConstant


def test_power_int_values():
    v0 = IntVariable(2)
    v1 = IntVariable(3)
    v2 = v0 ** v1
    assert v2.value == 8

    v0.value = 3
    assert v2.value == 27


def test_power_int_value_to_int():
    v0 = IntVariable(2)
    v2 = v0 ** 3
    assert v2.value == 8

    v0.value = 3
    assert v2.value == 27


def test_power_int_to_int_value():
    v1 = IntVariable(3)
    v2 = 2 ** v1
    assert v2.value == 8

    v1.value = 4
    assert v2.value == 16


def test_power_constant_to_constant():
    v0 = IntConstant(2)
    v1 = IntConstant(3)
    v2 = v0 ** v1
    assert v2.value == 8
    assert isinstance(v2, IntConstant)


def test_power_literal_to_constant():
    v0 = IntConstant(2)
    v2 = 3 ** v0
    assert v2.value == 9
    assert isinstance(v2, IntConstant)


def test_power_constant_to_literal():
    v0 = IntConstant(2)
    v2 = v0 ** 3
    assert v2.value == 8
    assert isinstance(v2, IntConstant)
