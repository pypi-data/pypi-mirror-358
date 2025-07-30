from spellbind import float_values
from spellbind.float_values import FloatVariable, ManyFloatsToFloatValue, FloatConstant
from spellbind.int_values import IntVariable


def test_add_float_values():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = v0 + v1
    assert v2.value == 4.0

    v0.value = 3.5
    assert v2.value == 6.0


def test_add_float_value_plus_float():
    v0 = FloatVariable(1.5)
    v2 = v0 + 2.5
    assert v2.value == 4.0

    v0.value = 3.5
    assert v2.value == 6.0


def test_add_float_value_plus_int():
    v0 = FloatVariable(1.5)
    v2 = v0 + 2
    assert v2.value == 3.5

    v0.value = 3.5
    assert v2.value == 5.5


def test_add_float_value_plus_int_value():
    v0 = FloatVariable(1.5)
    v1 = IntVariable(2)
    v2 = v0 + v1
    assert v2.value == 3.5

    v0.value = 3.5
    assert v2.value == 5.5


def test_add_float_plus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 1.5 + v1
    assert v2.value == 4.0

    v1.value = 3.5
    assert v2.value == 5.0


def test_add_int_plus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 2 + v1
    assert v2.value == 4.5

    v1.value = 3.5
    assert v2.value == 5.5


def test_add_many_values_waterfall_style_are_combined():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    v3 = FloatVariable(4.5)

    v4 = v0 + v1 + v2 + v3
    assert v4.value == 12.0

    assert isinstance(v4, ManyFloatsToFloatValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_add_many_values_grouped_are_combined():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    v3 = FloatVariable(4.5)

    v4 = (v0 + v1) + (v2 + v3)
    assert v4.value == 12.0

    assert isinstance(v4, ManyFloatsToFloatValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_add_constant_to_literal_is_constant():
    v0 = FloatConstant(1.5)
    v1 = 2.5
    v2 = v0 + v1
    assert v2.value == 4.0
    assert isinstance(v2, FloatConstant)


def test_add_constant_to_constant_is_constant():
    v0 = FloatConstant(1.5)
    v1 = FloatConstant(2.5)
    v2 = v0 + v1
    assert v2.value == 4.0
    assert isinstance(v2, FloatConstant)


def test_add_literal_to_constant_is_constant():
    v0 = 1.5
    v1 = FloatConstant(2.5)
    v2 = v0 + v1
    assert v2.value == 4.0
    assert isinstance(v2, FloatConstant)


def test_sum_float_values():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = FloatVariable(3.5)
    summed = float_values.sum_floats(v0, v1, v2)
    assert summed.value == 7.5

    v0.value = 2.5
    assert summed.value == 8.5


def test_sum_float_constants():
    v0 = FloatConstant(1.5)
    v1 = FloatConstant(2.5)
    v2 = FloatConstant(3.5)
    summed = float_values.sum_floats(v0, v1, v2)
    assert summed.constant_value_or_raise == 7.5
