from spellbind.float_values import FloatVariable, FloatConstant


def test_float_pos():
    var = FloatVariable(3.14)
    result = +var
    assert result is var
    assert result.value == 3.14


def test_float_pos_negative():
    var = FloatVariable(-2.5)
    result = +var
    assert result is var
    assert result.value == -2.5


def test_float_pos_constant_is_constant():
    const = FloatConstant(3.14)
    result = +const
    assert result is const
    assert result.value == 3.14
