from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_less_than_float_values():
    v0 = FloatVariable(3.5)
    v1 = FloatVariable(5.2)
    v2 = v0 < v1
    assert v2.value

    v0.value = 7.1
    assert not v2.value


def test_less_than_float_value_and_int():
    v0 = FloatVariable(3.5)
    v2 = v0 < 5
    assert v2.value

    v0.value = 7.1
    assert not v2.value


def test_less_than_float_value_and_float():
    v0 = FloatVariable(3.5)
    v2 = v0 < 5.2
    assert v2.value

    v0.value = 7.1
    assert not v2.value


def test_less_than_float_value_and_int_value():
    v0 = FloatVariable(3.5)
    v1 = IntVariable(5)
    v2 = v0 < v1
    assert v2.value

    v0.value = 7.1
    assert not v2.value


# Float Comparison Tests - Less Than or Equal
def test_less_than_or_equal_float_values():
    v0 = FloatVariable(3.5)
    v1 = FloatVariable(3.5)
    v2 = v0 <= v1
    assert v2.value

    v0.value = 4.1
    assert not v2.value


def test_less_than_or_equal_float_value_and_int():
    v0 = FloatVariable(3.5)
    v2 = v0 <= 4
    assert v2.value

    v0.value = 4.1
    assert not v2.value


def test_less_than_or_equal_float_value_and_float():
    v0 = FloatVariable(3.5)
    v2 = v0 <= 3.5
    assert v2.value

    v0.value = 4.1
    assert not v2.value


def test_less_than_or_equal_float_value_and_int_value():
    v0 = FloatVariable(3.5)
    v1 = IntVariable(4)
    v2 = v0 <= v1
    assert v2.value

    v0.value = 4.1
    assert not v2.value


# Float Comparison Tests - Greater Than
def test_greater_than_float_values():
    v0 = FloatVariable(7.2)
    v1 = FloatVariable(5.1)
    v2 = v0 > v1
    assert v2.value

    v0.value = 3.5
    assert not v2.value


def test_greater_than_float_value_and_int():
    v0 = FloatVariable(7.2)
    v2 = v0 > 5
    assert v2.value

    v0.value = 3.5
    assert not v2.value


def test_greater_than_float_value_and_float():
    v0 = FloatVariable(7.2)
    v2 = v0 > 5.1
    assert v2.value

    v0.value = 3.5
    assert not v2.value


def test_greater_than_float_value_and_int_value():
    v0 = FloatVariable(7.2)
    v1 = IntVariable(5)
    v2 = v0 > v1
    assert v2.value

    v0.value = 3.5
    assert not v2.value


# Float Comparison Tests - Greater Than or Equal
def test_greater_than_or_equal_float_values():
    v0 = FloatVariable(5.5)
    v1 = FloatVariable(5.5)
    v2 = v0 >= v1
    assert v2.value

    v0.value = 3.2
    assert not v2.value


def test_greater_than_or_equal_float_value_and_int():
    v0 = FloatVariable(5.5)
    v2 = v0 >= 5
    assert v2.value

    v0.value = 3.2
    assert not v2.value


def test_greater_than_or_equal_float_value_and_float():
    v0 = FloatVariable(5.5)
    v2 = v0 >= 4.8
    assert v2.value

    v0.value = 3.2
    assert not v2.value


def test_greater_than_or_equal_float_value_and_int_value():
    v0 = FloatVariable(5.5)
    v1 = IntVariable(5)
    v2 = v0 >= v1
    assert v2.value

    v0.value = 3.2
    assert not v2.value
