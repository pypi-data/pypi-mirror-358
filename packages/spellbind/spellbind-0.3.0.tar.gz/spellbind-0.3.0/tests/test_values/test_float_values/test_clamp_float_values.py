from spellbind.float_values import FloatVariable, FloatConstant


def test_clamp_float_values_in_range():
    value = FloatVariable(15.5)
    min_val = FloatVariable(10.0)
    max_val = FloatVariable(20.0)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15.5


def test_clamp_float_values_below_min():
    value = FloatVariable(5.2)
    min_val = FloatVariable(10.0)
    max_val = FloatVariable(20.0)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 10.0


def test_clamp_float_values_above_max():
    value = FloatVariable(25.8)
    min_val = FloatVariable(10.0)
    max_val = FloatVariable(20.0)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 20.0


def test_clamp_float_values_with_literals_in_range():
    value = FloatVariable(15.5)

    clamped = value.clamp(10.0, 20.0)
    assert clamped.value == 15.5


def test_clamp_float_values_with_literals_below_min():
    value = FloatVariable(5.2)

    clamped = value.clamp(10.0, 20.0)
    assert clamped.value == 10.0


def test_clamp_float_values_with_literals_above_max():
    value = FloatVariable(25.8)

    clamped = value.clamp(10.0, 20.0)
    assert clamped.value == 20.0


def test_clamp_float_values_reactive_value_changes():
    value = FloatVariable(15.5)
    min_val = FloatVariable(10.0)
    max_val = FloatVariable(20.0)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15.5

    value.value = 5.2
    assert clamped.value == 10.0

    value.value = 25.8
    assert clamped.value == 20.0

    value.value = 12.3
    assert clamped.value == 12.3


def test_clamp_float_values_reactive_bounds_changes():
    value = FloatVariable(15.5)
    min_val = FloatVariable(10.0)
    max_val = FloatVariable(20.0)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15.5

    min_val.value = 18.0
    assert clamped.value == 18.0

    min_val.value = 11.0
    assert clamped.value == 15.5

    max_val.value = 12.0
    assert clamped.value == 12.0


def test_clamp_middle_three_constants_is_constant():
    value = FloatConstant(15.5)
    min_val = FloatConstant(10.0)
    max_val = FloatConstant(20.0)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, FloatConstant)
    assert clamped.value == 15.5


def test_clamp_lower_three_constants_is_constant():
    value = FloatConstant(5.2)
    min_val = FloatConstant(10.0)
    max_val = FloatConstant(20.0)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, FloatConstant)
    assert clamped.value == 10.0


def test_clamp_upper_three_constants_is_constant():
    value = FloatConstant(25.8)
    min_val = FloatConstant(10.0)
    max_val = FloatConstant(20.0)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, FloatConstant)
    assert clamped.value == 20.0
