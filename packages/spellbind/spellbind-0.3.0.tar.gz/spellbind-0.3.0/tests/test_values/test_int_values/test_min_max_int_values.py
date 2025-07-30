from spellbind import int_values
from spellbind.int_values import IntConstant
from spellbind.values import SimpleVariable


def test_min_int_values():
    a = SimpleVariable(10)
    b = SimpleVariable(20)
    c = SimpleVariable(5)

    min_val = int_values.min_int(a, b, c)
    assert min_val.value == 5

    c.value = 2
    assert min_val.value == 2


def test_min_int_values_with_literals():
    a = SimpleVariable(10)

    min_val = int_values.min_int(a, 25, 15)
    assert min_val.value == 10

    a.value = 5
    assert min_val.value == 5


def test_min_int_constants_is_constant():
    a = IntConstant(10)
    b = IntConstant(20)
    c = IntConstant(5)

    min_val = int_values.min_int(a, b, c)
    assert isinstance(min_val, IntConstant)


def test_max_int_values():
    a = SimpleVariable(10)
    b = SimpleVariable(20)
    c = SimpleVariable(5)

    max_val = int_values.max_int(a, b, c)
    assert max_val.value == 20

    a.value = 30
    assert max_val.value == 30


def test_max_int_values_with_literals():
    a = SimpleVariable(10)

    max_val = int_values.max_int(a, 25, 15)
    assert max_val.value == 25

    a.value = 30
    assert max_val.value == 30


def test_max_int_constants_is_constant():
    a = IntConstant(10)
    b = IntConstant(20)
    c = IntConstant(5)

    max_val = int_values.max_int(a, b, c)
    assert isinstance(max_val, IntConstant)
