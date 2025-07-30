from spellbind.float_values import FloatConstant


def test_get_cached_constants_are_same():
    v0 = FloatConstant.of(12.)
    v1 = FloatConstant.of(12.)
    assert v0 is v1


def test_get_non_cached_constant_are_different():
    v0 = FloatConstant.of(123456.)
    v1 = FloatConstant.of(123456.)
    assert v0 is not v1


def test_float_constant_of_int_and_float_are_same():
    v0 = FloatConstant.of(12)
    v1 = FloatConstant.of(12.)
    assert v0 is v1
