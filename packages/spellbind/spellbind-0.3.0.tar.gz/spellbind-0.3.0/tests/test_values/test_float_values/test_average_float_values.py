from spellbind import float_values
from spellbind.float_values import FloatVariable, FloatConstant


def test_min_float_values():
    v0 = FloatVariable(1.)
    v1 = FloatVariable(2.)
    v2 = FloatVariable(3.)

    average_val = float_values.average_floats(v0, v1, v2)
    assert average_val.value == 2.

    v2.value = 6.
    assert average_val.value == 3.


def test_min_float_values_with_literals():
    v0 = FloatVariable(1.)

    average_val = float_values.average_floats(v0, 2., 3.)
    assert average_val.value == 2.

    v0.value = 4.
    assert average_val.value == 3.


def test_min_int_constants_is_constant():
    v0 = FloatConstant(1)
    v1 = FloatConstant(2)
    v2 = FloatConstant(3)

    average_val = float_values.average_floats(v0, v1, v2)
    assert isinstance(average_val, FloatConstant)


def test_sum_averaged_float_values():
    v0 = FloatVariable(1.)
    v1 = FloatVariable(2.)
    v2 = FloatVariable(3.)

    average_val_0 = float_values.average_floats(v0, v1, v2)

    v3 = FloatVariable(4.)
    v4 = FloatVariable(5.)
    average_val_1 = float_values.average_floats(v3, v4)
    summed_average = average_val_0 + average_val_1

    assert summed_average.value == (1. + 2. + 3.) / 3. + (4. + 5.) / 2.
