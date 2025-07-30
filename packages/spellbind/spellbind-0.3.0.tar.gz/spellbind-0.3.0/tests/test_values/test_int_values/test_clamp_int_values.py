from spellbind.int_values import IntVariable, IntConstant


def test_clamp_int_values_in_range():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15


def test_clamp_int_values_below_min():
    value = IntVariable(5)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 10


def test_clamp_int_values_above_max():
    value = IntVariable(25)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 20


def test_clamp_int_values_with_literals_in_range():
    value = IntVariable(15)

    clamped = value.clamp(10, 20)
    assert clamped.value == 15


def test_clamp_int_values_with_literals_below_min():
    value = IntVariable(5)

    clamped = value.clamp(10, 20)
    assert clamped.value == 10


def test_clamp_int_values_with_literals_above_max():
    value = IntVariable(25)

    clamped = value.clamp(10, 20)
    assert clamped.value == 20


def test_clamp_int_values_reactive_value_changes():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15

    value.value = 5
    assert clamped.value == 10

    value.value = 25
    assert clamped.value == 20

    value.value = 12
    assert clamped.value == 12


def test_clamp_int_values_reactive_bounds_changes():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15

    min_val.value = 18
    assert clamped.value == 18

    min_val.value = 11
    assert clamped.value == 15

    max_val.value = 12
    assert clamped.value == 12


def test_clamp_middle_three_constants_is_constant():
    value = IntConstant(15)
    min_val = IntConstant(10)
    max_val = IntConstant(20)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, IntConstant)
    assert clamped.value == 15


def test_clamp_lower_three_constants_is_constant():
    value = IntConstant(5)
    min_val = IntConstant(10)
    max_val = IntConstant(20)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, IntConstant)
    assert clamped.value == 10


def test_clamp_upper_three_constants_is_constant():
    value = IntConstant(25)
    min_val = IntConstant(10)
    max_val = IntConstant(20)

    clamped = value.clamp(min_val, max_val)
    assert isinstance(clamped, IntConstant)
    assert clamped.value == 20
