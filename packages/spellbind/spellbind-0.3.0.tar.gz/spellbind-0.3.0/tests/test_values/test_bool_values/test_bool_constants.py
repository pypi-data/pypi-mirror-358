from spellbind import bool_values
from spellbind.bool_values import BoolConstant


def test_bool_constant_true_to_str():
    const = BoolConstant(True)
    assert str(const) == "True"


def test_bool_constant_false_to_str():
    const_false = BoolConstant(False)
    assert str(const_false) == "False"


def test_bool_constant_of_true():
    const_true = BoolConstant.of(True)
    assert const_true is bool_values.TRUE


def test_bool_constant_of_false():
    const_false = BoolConstant.of(False)
    assert const_false is bool_values.FALSE


def test_bool_constant_not_true_is_false():
    not_true = BoolConstant.of(True).logical_not
    assert not_true is bool_values.FALSE


def test_bool_constant_not_false_is_true():
    not_false = BoolConstant.of(False).logical_not
    assert not_false is bool_values.TRUE
