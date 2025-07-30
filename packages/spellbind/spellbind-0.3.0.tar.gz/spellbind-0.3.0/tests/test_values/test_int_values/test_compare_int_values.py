from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_less_than_int_values():
    v0 = IntVariable(3)
    v1 = IntVariable(5)
    v2 = v0 < v1
    assert v2.value

    v0.value = 7
    assert not v2.value


def test_less_than_int_value_and_int():
    v0 = IntVariable(3)
    v2 = v0 < 5
    assert v2.value

    v0.value = 7
    assert not v2.value


def test_less_than_int_value_and_float():
    v0 = IntVariable(3)
    v2 = v0 < 5.5
    assert v2.value

    v0.value = 6
    assert not v2.value


def test_less_than_int_value_and_float_value():
    v0 = IntVariable(3)
    v1 = FloatVariable(5.5)
    v2 = v0 < v1
    assert v2.value

    v0.value = 6
    assert not v2.value


# Comparison Tests - Less Than or Equal
def test_less_than_or_equal_int_values():
    v0 = IntVariable(3)
    v1 = IntVariable(3)
    v2 = v0 <= v1
    assert v2.value

    v0.value = 4
    assert not v2.value


def test_less_than_or_equal_int_value_and_int():
    v0 = IntVariable(3)
    v2 = v0 <= 3
    assert v2.value

    v0.value = 4
    assert not v2.value


def test_less_than_or_equal_int_value_and_float():
    v0 = IntVariable(3)
    v2 = v0 <= 3.5
    assert v2.value

    v0.value = 4
    assert not v2.value


def test_less_than_or_equal_int_value_and_float_value():
    v0 = IntVariable(3)
    v1 = FloatVariable(3.5)
    v2 = v0 <= v1
    assert v2.value

    v0.value = 4
    assert not v2.value


# Comparison Tests - Greater Than
def test_greater_than_int_values():
    v0 = IntVariable(7)
    v1 = IntVariable(5)
    v2 = v0 > v1
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_int_value_and_int():
    v0 = IntVariable(7)
    v2 = v0 > 5
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_int_value_and_float():
    v0 = IntVariable(7)
    v2 = v0 > 5.5
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_int_value_and_float_value():
    v0 = IntVariable(7)
    v1 = FloatVariable(5.5)
    v2 = v0 > v1
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_or_equal_int_values():
    v0 = IntVariable(5)
    v1 = IntVariable(5)
    v2 = v0 >= v1
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_or_equal_int_value_and_int():
    v0 = IntVariable(5)
    v2 = v0 >= 5
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_or_equal_int_value_and_float():
    v0 = IntVariable(5)
    v2 = v0 >= 4.5
    assert v2.value

    v0.value = 3
    assert not v2.value


def test_greater_than_or_equal_int_value_and_float_value():
    v0 = IntVariable(5)
    v1 = FloatVariable(4.5)
    v2 = v0 >= v1
    assert v2.value

    v0.value = 3
    assert not v2.value
