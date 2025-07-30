from spellbind.int_values import IntConstant, IntVariable, IntValue


def test_int_constant_str():
    const = IntConstant(42)
    assert str(const) == "42"


def test_map_derived_int_value_to_list():
    value0 = IntVariable(2)
    value1 = IntConstant(3)
    added = value0 + value1
    mapped_value = added.map(lambda x: ["foo"]*x)

    assert mapped_value.value == ["foo", "foo", "foo", "foo", "foo"]


def test_int_const_repr():
    const = IntConstant(42)
    assert repr(const) == "IntConstant(42)"


def test_derive_int_constant_returns_constant():
    v0 = IntConstant(4)
    derived = IntValue.derive_from_one(lambda x: x + 1, v0)
    assert derived.constant_value_or_raise == 5


def test_derive_int_literal_returns_constant():
    derived = IntValue.derive_from_one(lambda x: x + 1, 4)
    assert derived.constant_value_or_raise == 5
