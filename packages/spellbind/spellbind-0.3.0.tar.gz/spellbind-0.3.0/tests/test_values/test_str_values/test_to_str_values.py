from spellbind.bool_values import BoolVariable
from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable
from spellbind.str_values import StrVariable
from spellbind.values import SimpleVariable


def test_to_str_of_list():
    value = SimpleVariable([1, 2, 3])
    to_str_value = value.to_str()

    assert to_str_value.value == "[1, 2, 3]"

    value.value = ["a", "b"]

    assert to_str_value.value == "['a', 'b']"


def test_to_str_of_int():
    value = IntVariable(42)
    to_str_value = value.to_str()

    assert to_str_value.value == "42"

    value.value = 100
    assert to_str_value.value == "100"


def test_to_str_of_float():
    value = FloatVariable(3.14)
    to_str_value = value.to_str()

    assert to_str_value.value == "3.14"

    value.value = 2.718
    assert to_str_value.value == "2.718"


def test_to_str_of_bool_true():
    value = BoolVariable(True)
    to_str_value = value.to_str()

    assert to_str_value.value == "True"

    value.value = False
    assert to_str_value.value == "False"


def test_to_str_of_bool_false():
    value = BoolVariable(False)
    to_str_value = value.to_str()

    assert to_str_value.value == "False"

    value.value = True
    assert to_str_value.value == "True"


def test_to_str_of_str_returns_same_object():
    value = StrVariable("hello")
    to_str_value = value.to_str()

    assert to_str_value is value
