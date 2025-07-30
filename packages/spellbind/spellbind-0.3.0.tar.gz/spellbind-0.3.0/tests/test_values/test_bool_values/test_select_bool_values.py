from spellbind.int_values import IntVariable, IntValue
from spellbind.str_values import StrVariable, StrValue
from spellbind.bool_values import BoolVariable, BoolValue
from spellbind.float_values import FloatVariable, FloatValue
from spellbind.values import SimpleVariable, Value


def test_select_int_bool_true_selects_first():
    condition = BoolVariable(True)
    first = IntVariable(10)
    second = IntVariable(20)
    result = condition.select(first, second)
    assert result.value == 10

    condition.value = False
    assert result.value == 20


def test_select_int_bool_false_selects_second():
    condition = BoolVariable(False)
    first = IntVariable(10)
    second = IntVariable(20)
    result = condition.select(first, second)
    assert result.value == 20

    condition.value = True
    assert result.value == 10


def test_select_int_bool_true_change_first_variable():
    condition = BoolVariable(True)
    first = IntVariable(10)
    second = IntVariable(20)
    result = condition.select(first, second)
    assert result.value == 10

    first.value = 30
    assert result.value == 30


def test_select_int_bool_false_change_first_variable():
    condition = BoolVariable(False)
    first = IntVariable(10)
    second = IntVariable(20)
    result = condition.select(first, second)
    assert result.value == 20

    first.value = 30
    assert result.value == 20


def test_select_int_variable_variable_returns_int_value():
    condition = BoolVariable(True)
    first = IntVariable(10)
    second = IntVariable(20)
    result = condition.select(first, second)
    assert isinstance(result, IntValue)


def test_select_int_literal_variable_returns_int_value():
    condition = BoolVariable(True)
    second = IntVariable(20)
    result = condition.select(10, second)
    assert isinstance(result, IntValue)


def test_select_int_variable_literal_returns_int_value():
    condition = BoolVariable(True)
    first = IntVariable(10)
    result = condition.select(first, 20)
    assert isinstance(result, IntValue)


def test_select_int_literal_literal_returns_int_value():
    condition = BoolVariable(True)
    result = condition.select(10, 20)
    assert isinstance(result, IntValue)


def test_select_str_bool_true_selects_first():
    condition = BoolVariable(True)
    first = StrVariable("hello")
    second = StrVariable("world")
    result = condition.select(first, second)
    assert result.value == "hello"

    condition.value = False
    assert result.value == "world"


def test_select_str_bool_false_selects_second():
    condition = BoolVariable(False)
    first = StrVariable("hello")
    second = StrVariable("world")
    result = condition.select(first, second)
    assert result.value == "world"

    condition.value = True
    assert result.value == "hello"


def test_select_str_bool_true_change_first_variable():
    condition = BoolVariable(True)
    first = StrVariable("hello")
    second = StrVariable("world")
    result = condition.select(first, second)
    assert result.value == "hello"

    first.value = "goodbye"
    assert result.value == "goodbye"


def test_select_str_bool_false_change_first_variable():
    condition = BoolVariable(False)
    first = StrVariable("hello")
    second = StrVariable("world")
    result = condition.select(first, second)
    assert result.value == "world"

    first.value = "goodbye"
    assert result.value == "world"


def test_select_str_variable_variable_returns_str_value():
    condition = BoolVariable(True)
    first = StrVariable("hello")
    second = StrVariable("world")
    result = condition.select(first, second)
    assert isinstance(result, StrValue)


def test_select_str_literal_variable_returns_str_value():
    condition = BoolVariable(True)
    second = StrVariable("world")
    result = condition.select("hello", second)
    assert isinstance(result, StrValue)


def test_select_str_variable_literal_returns_str_value():
    condition = BoolVariable(True)
    first = StrVariable("hello")
    result = condition.select(first, "world")
    assert isinstance(result, StrValue)


def test_select_str_literal_literal_returns_str_value():
    condition = BoolVariable(True)
    result = condition.select("hello", "world")
    assert isinstance(result, StrValue)


def test_select_float_bool_true_selects_first():
    condition = BoolVariable(True)
    first = FloatVariable(1.5)
    second = FloatVariable(2.5)
    result = condition.select(first, second)
    assert result.value == 1.5

    condition.value = False
    assert result.value == 2.5


def test_select_float_bool_false_selects_second():
    condition = BoolVariable(False)
    first = FloatVariable(1.5)
    second = FloatVariable(2.5)
    result = condition.select(first, second)
    assert result.value == 2.5

    condition.value = True
    assert result.value == 1.5


def test_select_float_bool_true_change_first_variable():
    condition = BoolVariable(True)
    first = FloatVariable(1.5)
    second = FloatVariable(2.5)
    result = condition.select(first, second)
    assert result.value == 1.5

    first.value = 3.5
    assert result.value == 3.5


def test_select_float_bool_false_change_first_variable():
    condition = BoolVariable(False)
    first = FloatVariable(1.5)
    second = FloatVariable(2.5)
    result = condition.select(first, second)
    assert result.value == 2.5

    first.value = 3.5
    assert result.value == 2.5


def test_select_float_variable_variable_returns_float_value():
    condition = BoolVariable(True)
    first = FloatVariable(1.5)
    second = FloatVariable(2.5)
    result = condition.select(first, second)
    assert isinstance(result, FloatValue)


def test_select_float_literal_variable_returns_float_value():
    condition = BoolVariable(True)
    second = FloatVariable(2.5)
    result = condition.select(1.5, second)
    assert isinstance(result, FloatValue)


def test_select_float_variable_literal_returns_float_value():
    condition = BoolVariable(True)
    first = FloatVariable(1.5)
    result = condition.select(first, 2.5)
    assert isinstance(result, FloatValue)


def test_select_float_literal_literal_returns_float_value():
    condition = BoolVariable(True)
    result = condition.select(1.5, 2.5)
    assert isinstance(result, FloatValue)


def test_select_bool_bool_true_selects_first():
    condition = BoolVariable(True)
    first = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(first, second)
    assert result.value

    condition.value = False
    assert not result.value


def test_select_bool_bool_false_selects_second():
    condition = BoolVariable(False)
    first = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(first, second)
    assert not result.value

    condition.value = True
    assert result.value


def test_select_bool_bool_true_change_first_variable():
    condition = BoolVariable(True)
    first = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(first, second)
    assert result.value

    first.value = False
    assert not result.value


def test_select_bool_bool_false_change_first_variable():
    condition = BoolVariable(False)
    first = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(first, second)
    assert not result.value

    first.value = False
    assert not result.value


def test_select_bool_variable_variable_returns_bool_value():
    condition = BoolVariable(True)
    first = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(first, second)
    assert isinstance(result, BoolValue)


def test_select_bool_literal_variable_returns_bool_value():
    condition = BoolVariable(True)
    second = BoolVariable(False)
    result = condition.select(True, second)
    assert isinstance(result, BoolValue)


def test_select_bool_variable_literal_returns_bool_value():
    condition = BoolVariable(True)
    first = BoolVariable(True)
    result = condition.select(first, False)
    assert isinstance(result, BoolValue)


def test_select_bool_literal_literal_returns_bool_value():
    condition = BoolVariable(True)
    result = condition.select(True, False)
    assert isinstance(result, BoolValue)


def test_select_list_str_bool_true_selects_first():
    condition = BoolVariable(True)
    first = SimpleVariable(["a", "b"])
    second = SimpleVariable(["c", "d"])
    result = condition.select(first, second)
    assert result.value == ["a", "b"]

    condition.value = False
    assert result.value == ["c", "d"]


def test_select_list_str_bool_false_selects_second():
    condition = BoolVariable(False)
    first = SimpleVariable(["a", "b"])
    second = SimpleVariable(["c", "d"])
    result = condition.select(first, second)
    assert result.value == ["c", "d"]

    condition.value = True
    assert result.value == ["a", "b"]


def test_select_list_str_bool_true_change_first_variable():
    condition = BoolVariable(True)
    first = SimpleVariable(["a", "b"])
    second = SimpleVariable(["c", "d"])
    result = condition.select(first, second)
    assert result.value == ["a", "b"]

    first.value = ["e", "f"]
    assert result.value == ["e", "f"]


def test_select_list_str_bool_false_change_first_variable():
    condition = BoolVariable(False)
    first = SimpleVariable(["a", "b"])
    second = SimpleVariable(["c", "d"])
    result = condition.select(first, second)
    assert result.value == ["c", "d"]

    first.value = ["e", "f"]
    assert result.value == ["c", "d"]


def test_select_list_str_variable_variable_returns_value():
    condition = BoolVariable(True)
    first = SimpleVariable(["a", "b"])
    second = SimpleVariable(["c", "d"])
    result = condition.select(first, second)
    assert isinstance(result, Value)


def test_select_list_str_literal_variable_returns_value():
    condition = BoolVariable(True)
    second = SimpleVariable(["c", "d"])
    result = condition.select(["a", "b"], second)
    assert isinstance(result, Value)


def test_select_list_str_variable_literal_returns_value():
    condition = BoolVariable(True)
    first = SimpleVariable(["a", "b"])
    result = condition.select(first, ["c", "d"])
    assert isinstance(result, Value)


def test_select_list_str_literal_literal_returns_value():
    condition = BoolVariable(True)
    result = condition.select(["a", "b"], ["c", "d"])
    assert isinstance(result, Value)
