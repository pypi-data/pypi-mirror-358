import gc

from spellbind.float_values import FloatConstant, FloatVariable, FloatValue


def test_float_constant_str():
    const = FloatConstant(3.14)
    assert str(const) == "3.14"


def test_add_float_values_keeps_reference():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = v0 + v1
    assert len(v0._on_change._subscriptions) == 1
    gc.collect()

    v0.value = 3.5
    assert len(v0._on_change._subscriptions) == 1


def test_add_int_values_garbage_collected():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = v0 + v1
    assert len(v0._on_change._subscriptions) == 1
    assert len(v1._on_change._subscriptions) == 1
    v2 = None
    gc.collect()
    v0.value = 3.5  # trigger removal of weak references
    v1.value = 4.5  # trigger removal of weak references
    assert len(v0._on_change._subscriptions) == 0
    assert len(v1._on_change._subscriptions) == 0


def test_derive_float_constant_returns_constant():
    v0 = FloatConstant(4.5)
    derived = FloatValue.derive_from_one(lambda x: x + 1.0, v0)
    assert derived.constant_value_or_raise == 5.5


def test_derive_float_literal_returns_constant():
    derived = FloatValue.derive_from_one(lambda x: x + 1.0, 4.5)
    assert derived.constant_value_or_raise == 5.5
