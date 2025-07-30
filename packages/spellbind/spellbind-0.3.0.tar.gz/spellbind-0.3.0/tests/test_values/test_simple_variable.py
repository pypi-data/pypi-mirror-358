import gc

import pytest

from spellbind.bool_values import BoolValue
from spellbind.float_values import FloatValue
from spellbind.int_values import IntValue
from spellbind.str_values import StrValue
from spellbind.values import SimpleVariable, Constant
from conftest import NoParametersObserver, OneParameterObserver


def test_simple_variable_constructor():
    variable = SimpleVariable("initial_value")
    assert variable.value == "initial_value"


def test_simple_variable_set_same_value():
    variable = SimpleVariable("test")
    observer = OneParameterObserver()

    variable.observe(observer)
    variable.value = "test"

    observer.assert_not_called()


def test_simple_variable_set_different_value():
    variable = SimpleVariable("initial")
    observer = OneParameterObserver()

    variable.observe(observer)
    variable.value = "changed"

    assert variable.value == "changed"
    observer.assert_called_once_with("changed")


def test_simple_variable_unobserve():
    variable = SimpleVariable("test")
    observer = OneParameterObserver()

    variable.observe(observer)
    variable.unobserve(observer)
    variable.value = "changed"

    observer.assert_not_called()


def test_simple_variable_multiple_observers():
    variable = SimpleVariable(1)
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()

    variable.observe(observer0)
    variable.observe(observer1)
    variable.value = 2

    observer0.assert_called_once_with()
    observer1.assert_called_once_with(2)


def test_simple_variable_observe_lambda():
    variable = SimpleVariable("start")
    calls = []

    variable.observe(lambda value: calls.append(value))
    variable.value = "end"

    assert calls == ["end"]


def test_simple_variable_unobserve_lambda():
    variable = SimpleVariable(5)
    calls = []
    observer = lambda value: calls.append(value)

    variable.observe(observer)
    variable.value = 10
    variable.unobserve(observer)
    variable.value = 15

    assert calls == [10]


def test_simple_variable_bind_twice_to_same():
    variable = SimpleVariable("test")
    constant = Constant("value")

    variable.bind_to(constant)
    variable.bind_to(constant, already_bound_ok=True)

    assert variable.value == "value"


def test_simple_variable_bind_to_constant():
    variable = SimpleVariable("old")
    constant = Constant("new")

    variable.bind_to(constant)

    assert variable.value == "new"


def test_simple_variable_bind_to_simple_variable():
    variable1 = SimpleVariable(100)
    variable2 = SimpleVariable(200)

    variable1.bind_to(variable2)

    assert variable1.value == 200


def test_simple_variable_bind_already_bound_error():
    variable = SimpleVariable("test")
    constant1 = Constant("value1")
    constant2 = Constant("value2")

    variable.bind_to(constant1)

    with pytest.raises(ValueError):
        variable.bind_to(constant2)


def test_simple_variable_bind_already_bound_ok():
    variable = SimpleVariable("test")
    constant1 = Constant("value1")
    constant2 = Constant("value2")

    variable.bind_to(constant1)
    variable.bind_to(constant2, already_bound_ok=True)

    assert variable.value == "value2"


def test_simple_variable_change_after_unbind():
    variable = SimpleVariable("initial")
    constant = Constant("bound_value")

    variable.bind_to(constant)
    variable.unbind()
    variable.value = "after_unbind"

    assert variable.value == "after_unbind"


def test_simple_variable_change_without_unbind_raises():
    variable = SimpleVariable("initial")
    constant = Constant("bound_value")

    variable.bind_to(constant)
    with pytest.raises(ValueError):
        variable.value = "after_unbind"


def test_simple_variable_change_root_after_unbind():
    dependent = SimpleVariable("dependent")
    root = SimpleVariable("root")

    dependent.bind_to(root)
    dependent.unbind()
    root.value = "new_root_value"
    assert dependent.value == "root"


def test_simple_variable_unbind_not_bound_error():
    variable = SimpleVariable("test")

    with pytest.raises(ValueError):
        variable.unbind()


def test_simple_variable_unbind_not_bound_ok():
    variable = SimpleVariable("test")

    variable.unbind(not_bound_ok=True)

    assert variable.value == "test"


def test_simple_variable_bind_updates_value():
    variable = SimpleVariable(0)
    observer = OneParameterObserver()

    variable.observe(observer)
    constant = Constant(42)
    variable.bind_to(constant)

    observer.assert_called_once_with(42)


def test_simple_variable_bound_value_changes_propagate():
    variable1 = SimpleVariable("start")
    variable2 = SimpleVariable("initial")
    observer = OneParameterObserver()

    variable1.bind_to(variable2)
    variable1.observe(observer)
    variable2.value = "propagated"

    assert variable1.value == "propagated"
    observer.assert_called_once_with("propagated")


def test_simple_variable_unobserve_non_existent_observer():
    variable = SimpleVariable("test")
    observer = OneParameterObserver()

    with pytest.raises(ValueError):
        variable.unobserve(observer)


def test_simple_variable_bind_to_itself():
    variable = SimpleVariable("test")

    with pytest.raises(RecursionError):
        variable.bind_to(variable)


def test_simple_variable_set_value_while_bound_raises():
    variable = SimpleVariable("initial")
    constant = Constant("constant")

    variable.bind_to(constant)
    with pytest.raises(ValueError):
        variable.value = "manual_value"


def test_simple_variable_with_none_values():
    variable = SimpleVariable(None)
    observer = OneParameterObserver()

    variable.observe(observer)
    variable.value = "not_none"

    assert variable.value == "not_none"
    observer.assert_called_once_with("not_none")


def test_simple_variable_rebind_after_unbind():
    variable = SimpleVariable("start")
    constant1 = Constant("first")
    constant2 = Constant("second")

    variable.bind_to(constant1)
    variable.unbind()
    variable.bind_to(constant2)

    assert variable.value == "second"


def test_simple_variable_derived_from_empty():
    variable = SimpleVariable("test")

    assert variable.derived_from() == frozenset()


def test_simple_variable_derived_from_bound():
    variable = SimpleVariable("test")
    constant = Constant("bound")

    variable.bind_to(constant)

    assert variable.derived_from() == frozenset([constant])


def test_simple_variable_deep_derived_from_empty():
    variable = SimpleVariable("test")

    assert list(variable.deep_derived_from) == []


def test_simple_variable_deep_derived_from_single_level():
    variable = SimpleVariable("test")
    constant = Constant("bound")

    variable.bind_to(constant)

    assert list(variable.deep_derived_from) == [constant]


def test_simple_variable_deep_derived_from_two_levels():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    constant = Constant("bound")

    variable2.bind_to(constant)
    variable1.bind_to(variable2)

    dependencies = list(variable1.deep_derived_from)
    assert len(dependencies) == 2
    assert variable2 in dependencies
    assert constant in dependencies


def test_simple_variable_deep_derived_from_three_levels():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    variable3 = SimpleVariable("test3")
    constant = Constant("bound")

    variable3.bind_to(constant)
    variable2.bind_to(variable3)
    variable1.bind_to(variable2)

    dependencies = list(variable1.deep_derived_from)
    assert len(dependencies) == 3
    assert variable2 in dependencies
    assert variable3 in dependencies
    assert constant in dependencies


def test_simple_variable_deep_derived_from_circular_two_variables():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")

    variable1.bind_to(variable2)

    with pytest.raises(RecursionError):
        variable2.bind_to(variable1)


def test_simple_variable_deep_derived_from_circular_three_variables():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    variable3 = SimpleVariable("test3")

    variable1.bind_to(variable2)
    variable2.bind_to(variable3)

    with pytest.raises(RecursionError):
        variable3.bind_to(variable1)


def test_simple_variable_deep_derived_from_diamond_pattern():
    variable_top = SimpleVariable("top")
    variable_left = SimpleVariable("left")
    variable_right = SimpleVariable("right")
    variable_bottom = SimpleVariable("bottom")

    variable_left.bind_to(variable_top)
    variable_right.bind_to(variable_top)
    variable_bottom.bind_to(variable_left)
    variable_bottom.bind_to(variable_right, already_bound_ok=True)

    dependencies = list(variable_bottom.deep_derived_from)
    assert len(dependencies) == 2
    assert variable_right in dependencies
    assert variable_top in dependencies


def test_bind_weak_reference_clears():
    root_var = SimpleVariable("root0")
    dependent_var = SimpleVariable("")
    dependent_var.bind_to(root_var, bind_weakly=True)

    values = []
    dependent_var.observe(lambda value: values.append(value))

    root_var.value = "root1"
    dependent_var = None
    gc.collect()
    root_var.value = "root2"

    assert values == ["root1"]


def test_bind_strong_reference_stays():
    root_var = SimpleVariable("root0")
    dependent_var = SimpleVariable("")
    dependent_var.bind_to(root_var, bind_weakly=False)

    values = []
    dependent_var.observe(lambda value: values.append(value))

    root_var.value = "root1"
    dependent_var = None
    gc.collect()
    root_var.value = "root2"

    assert values == ["root1", "root2"]


def test_daisy_chain_variables_weak_reference_stays():
    root_var = SimpleVariable("root0")
    middle_var = SimpleVariable("")
    dependent_var = SimpleVariable("")

    middle_var.bind_to(root_var, bind_weakly=True)
    dependent_var.bind_to(middle_var, bind_weakly=False)

    values = []
    dependent_var.observe(lambda value: values.append(value))

    root_var.value = "root1"
    middle_var = None
    gc.collect()
    root_var.value = "root2"

    assert values == ["root1", "root2"]


def test_simple_int_variable_str():
    var_int = SimpleVariable(42)
    assert str(var_int) == "42"


def test_simple_str_variable_str():
    var_str = SimpleVariable("hello")
    assert str(var_str) == "hello"


def test_simple_float_variable_str():
    var_float = SimpleVariable(3.14)
    assert str(var_float) == "3.14"


def test_simple_bool_variable_str():
    var_bool = SimpleVariable(True)
    assert str(var_bool) == "True"


def test_simple_none_variable_str():
    none_bool = SimpleVariable(None)
    assert str(none_bool) == "None"


def test_map_float_to_int():
    value = SimpleVariable(42.5)
    mapped = value.map_to_int(int)

    assert isinstance(mapped, IntValue)
    assert mapped.value == 42

    value.value = 100.9
    assert mapped.value == 100


def test_map_int_to_float():
    value = SimpleVariable(42)
    mapped = value.map_to_float(float)

    assert isinstance(mapped, FloatValue)
    assert mapped.value == 42.0

    value.value = 100
    assert mapped.value == 100.0


def test_map_int_to_str():
    value = SimpleVariable(42)
    mapped = value.map_to_str(str)

    assert isinstance(mapped, StrValue)
    assert mapped.value == "42"

    value.value = 100
    assert mapped.value == "100"


def test_map_int_to_bool():
    value = SimpleVariable(0)
    mapped = value.map_to_bool(bool)

    assert isinstance(mapped, BoolValue)
    assert mapped.value is False

    value.value = 1
    assert mapped.value is True


def test_map_str_to_int():
    value = SimpleVariable("hello")
    mapped = value.map_to_int(len)

    assert isinstance(mapped, IntValue)
    assert mapped.value == 5

    value.value = "world!"
    assert mapped.value == 6
