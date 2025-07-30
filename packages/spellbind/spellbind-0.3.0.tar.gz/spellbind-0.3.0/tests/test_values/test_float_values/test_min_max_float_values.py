from spellbind import float_values
from spellbind.float_values import FloatConstant, FloatVariable, ManyFloatsToFloatValue
from spellbind.values import SimpleVariable


def test_min_float_values():
    v0 = SimpleVariable(10.5)
    v1 = SimpleVariable(20.3)
    v2 = SimpleVariable(5.7)

    min_val = float_values.min_float(v0, v1, v2)
    assert min_val.value == 5.7

    v2.value = 2.1
    assert min_val.value == 2.1


def test_min_float_values_with_literals():
    v0 = SimpleVariable(10.5)

    min_val = float_values.min_float(v0, 25.7, 15.2)
    assert min_val.value == 10.5

    v0.value = 5.1
    assert min_val.value == 5.1


def test_min_int_constants_is_constant():
    v0 = FloatConstant(10.5)
    v1 = FloatConstant(20.3)
    v2 = FloatConstant(5.7)

    min_val = float_values.min_float(v0, v1, v2)
    assert isinstance(min_val, FloatConstant)


def test_max_float_values():
    v0 = SimpleVariable(10.5)
    v1 = SimpleVariable(20.3)
    v2 = SimpleVariable(5.7)

    max_val = float_values.max_float(v0, v1, v2)
    assert max_val.value == 20.3

    v0.value = 30.1
    assert max_val.value == 30.1


def test_max_float_values_with_literals():
    v0 = SimpleVariable(10.5)

    max_val = float_values.max_float(v0, 25.7, 15.2)
    assert max_val.value == 25.7

    v0.value = 30.1
    assert max_val.value == 30.1


def test_max_int_constants_is_constant():
    v0 = FloatConstant(10.5)
    v1 = FloatConstant(20.3)
    v2 = FloatConstant(5.7)

    max_val = float_values.max_float(v0, v1, v2)
    assert isinstance(max_val, FloatConstant)


def test_flattens_min_values():
    v0 = FloatVariable(10.5)
    v1 = FloatVariable(20.3)
    v2 = FloatVariable(5.7)

    min_val_0 = float_values.min_float(v0, v1, v2)

    v3 = FloatVariable(15.0)
    v4 = FloatVariable(25.0)
    min_val_1 = float_values.min_float(v3, v4)
    flattened_min_val = float_values.min_float(min_val_0, min_val_1)
    assert flattened_min_val.value == 5.7
    assert isinstance(flattened_min_val, ManyFloatsToFloatValue)
    assert flattened_min_val._input_values == (v0, v1, v2, v3, v4)


def test_flattens_max_values():
    v0 = FloatVariable(10.5)
    v1 = FloatVariable(20.3)
    v2 = FloatVariable(5.7)

    max_val_0 = float_values.max_float(v0, v1, v2)

    v3 = FloatVariable(15.0)
    v4 = FloatVariable(25.0)
    max_val_1 = float_values.max_float(v3, v4)
    flattened_max_val = float_values.max_float(max_val_0, max_val_1)
    assert flattened_max_val.value == 25.0
    assert isinstance(flattened_max_val, ManyFloatsToFloatValue)
    assert flattened_max_val._input_values == (v0, v1, v2, v3, v4)
