from spellbind.int_values import IntVariable, IntConstant


def test_int_pos():
    var = IntVariable(42)
    result = +var
    assert result is var
    assert result.value == 42


def test_int_pos_negative():
    var = IntVariable(-15)
    result = +var
    assert result is var
    assert result.value == -15


def test_float_pos_constant_is_constant():
    const = IntConstant(3)
    result = +const
    assert result is const
    assert result.value == 3
