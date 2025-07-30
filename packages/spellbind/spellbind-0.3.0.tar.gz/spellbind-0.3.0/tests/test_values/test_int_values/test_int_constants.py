from spellbind.int_values import IntConstant


def test_get_cached_constants_are_same():
    v0 = IntConstant.of(12)
    v1 = IntConstant.of(12)
    assert v0 is v1


def test_get_non_cached_constant_are_different():
    v0 = IntConstant.of(123456)
    v1 = IntConstant.of(123456)
    assert v0 is not v1
