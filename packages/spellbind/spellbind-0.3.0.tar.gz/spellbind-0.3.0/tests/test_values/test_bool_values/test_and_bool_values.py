import pytest

from spellbind.bool_values import BoolVariable, BoolConstant


@pytest.mark.parametrize("bool0, bool1", [(True, True), (True, False), (False, True), (False, False)])
def test_bool_variables_and(bool0, bool1):
    v0 = BoolVariable(bool0)
    v1 = BoolVariable(bool1)
    result = v0 & v1
    assert result.value is (bool0 and bool1)


@pytest.mark.parametrize("bool0, bool1", [(True, True), (True, False), (False, True), (False, False)])
def test_bool_variable_and_constant(bool0, bool1):
    v0 = BoolVariable(bool0)
    v1 = BoolConstant(bool1)
    result = v0 & v1
    assert result.value is (bool0 and bool1)


@pytest.mark.parametrize("bool0, bool1", [(True, True), (True, False), (False, True), (False, False)])
def test_bool_variable_and_literal(bool0, bool1):
    v0 = BoolVariable(bool0)
    result = v0 & bool1
    assert result.value is (bool0 and bool1)


@pytest.mark.parametrize("bool0, bool1", [(True, True), (True, False), (False, True), (False, False)])
def test_bool_literal_and_variable(bool0, bool1):
    v1 = BoolVariable(bool1)
    result = bool0 & v1
    assert result.value is (bool0 and bool1)


@pytest.mark.parametrize("bool0, bool1", [(True, True), (True, False), (False, True), (False, False)])
def test_bool_constant_and_constant_is_constant(bool0, bool1):
    v0 = BoolConstant(bool0)
    v1 = BoolConstant(bool1)
    result = v0 & v1
    assert result.value is (bool0 and bool1)
    assert isinstance(result, BoolConstant)
