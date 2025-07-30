from spellbind import float_values
from spellbind.float_values import FloatVariable, ManyFloatsToFloatValue, FloatConstant
from spellbind.int_values import IntVariable


def test_mul_float_values():
    v0 = FloatVariable(2.5)
    v1 = FloatVariable(3.0)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_mul_float_value_times_float():
    v0 = FloatVariable(2.5)
    v2 = v0 * 3.0
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_mul_float_value_times_int():
    v0 = FloatVariable(2.5)
    v2 = v0 * 3
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_mul_float_value_times_int_value():
    v0 = FloatVariable(2.5)
    v1 = IntVariable(3)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_mul_float_times_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2.5 * v1
    assert v2.value == 7.5

    v1.value = 4.0
    assert v2.value == 10.0


def test_mul_int_times_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2 * v1
    assert v2.value == 6.0

    v1.value = 4.0
    assert v2.value == 8.0


def test_mul_many_values_waterfall_style_are_combined():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    v3 = FloatVariable(4.5)

    v4 = v0 * v1 * v2 * v3
    assert v4.value == 59.0625

    assert isinstance(v4, ManyFloatsToFloatValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_mul_many_values_grouped_are_combined():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    v3 = FloatVariable(4.5)

    v4 = (v0 * v1) * (v2 * v3)
    assert v4.value == 59.0625

    assert isinstance(v4, ManyFloatsToFloatValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_mul_constant_by_literal_is_constant():
    v0 = FloatConstant(1.5)
    v1 = 2.5
    v2 = v0 * v1
    assert v2.value == 3.75
    assert isinstance(v2, FloatConstant)


def test_mul_constant_by_constant_is_constant():
    v0 = FloatConstant(1.5)
    v1 = FloatConstant(2.5)
    v2 = v0 * v1
    assert v2.value == 3.75
    assert isinstance(v2, FloatConstant)


def test_mul_literal_by_constant_is_constant():
    v0 = 1.5
    v1 = FloatConstant(2.5)
    v2 = v0 * v1
    assert v2.value == 3.75
    assert isinstance(v2, FloatConstant)


def test_multiply_float_values():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    v2 = float_values.multiply_floats(v0, v1, v2)
    assert v2.value == 13.125

    v0.value = 2.0
    assert v2.value == 17.5


def test_multiply_float_constants():
    v0 = FloatConstant(1.5)
    v1 = FloatConstant(2.5)
    v2 = FloatConstant(3.5)
    v2 = float_values.multiply_floats(v0, v1, v2)
    assert v2.constant_value_or_raise == 13.125
