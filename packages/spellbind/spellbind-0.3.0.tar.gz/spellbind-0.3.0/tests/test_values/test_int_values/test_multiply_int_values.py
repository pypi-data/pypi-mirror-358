from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable, ManyIntsToIntValue, IntConstant


def test_multiply_int_value_times_int():
    v0 = IntVariable(3)
    v2 = v0 * 4
    assert v2.value == 12

    v0.value = 5
    assert v2.value == 20


def test_multiply_int_value_times_float():
    v0 = IntVariable(3)
    v2 = v0 * 2.5
    assert v2.value == 7.5

    v0.value = 4
    assert v2.value == 10.0


def test_multiply_int_value_times_float_value():
    v0 = IntVariable(3)
    v1 = FloatVariable(2.5)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4
    assert v2.value == 10.0


def test_multiply_int_times_int_value():
    v1 = IntVariable(4)
    v2 = 3 * v1
    assert v2.value == 12

    v1.value = 5
    assert v2.value == 15


def test_multiply_float_times_int_value():
    v1 = IntVariable(4)
    v2 = 2.5 * v1
    assert v2.value == 10.0

    v1.value = 6
    assert v2.value == 15.0


def test_multiply_int_values():
    v0 = IntVariable(3)
    v1 = IntVariable(4)
    v2 = v0 * v1
    assert v2.value == 12

    v0.value = 5
    assert v2.value == 20


def test_multiply_many_values_waterfall_style_are_combined():
    v0 = IntVariable(1)
    v1 = IntVariable(2)
    v2 = IntVariable(3)
    v3 = IntVariable(4)

    v4 = v0 * v1 * v2 * v3
    assert v4.value == 24

    assert isinstance(v4, ManyIntsToIntValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_multiply_many_values_grouped_are_combined():
    v0 = IntVariable(1)
    v1 = IntVariable(2)
    v2 = IntVariable(3)
    v3 = IntVariable(4)

    v4 = (v0 * v1) * (v2 * v3)
    assert v4.value == 24

    assert isinstance(v4, ManyIntsToIntValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_multiply_constant_by_literal_is_constant():
    v0 = IntConstant(2)
    v1 = 3
    v2 = v0 * v1
    assert v2.value == 6
    assert isinstance(v2, IntConstant)


def test_multiply_constant_by_constant_is_constant():
    v0 = IntConstant(2)
    v1 = IntConstant(3)
    v2 = v0 * v1
    assert v2.value == 6
    assert isinstance(v2, IntConstant)


def test_multiply_literal_by_constant_is_constant():
    v0 = 2
    v1 = IntConstant(3)
    v2 = v0 * v1
    assert v2.value == 6
    assert isinstance(v2, IntConstant)
