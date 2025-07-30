import pytest
from spellbind.event import ValueEvent
from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver


def test_value_event_unobserve_nonexistent_mock_observer_fails():
    event = ValueEvent[str]()
    observer = OneParameterObserver()

    with pytest.raises(ValueError):
        event.unobserve(observer)


def test_value_event_observe_same_mock_observer_multiple_times():
    event = ValueEvent[str]()
    observer = OneParameterObserver()

    event.observe(observer)
    event.observe(observer)
    event("test")

    assert observer.call_count == 2


def test_value_event_call_with_no_observers():
    event = ValueEvent[str]()
    event("test_value")  # Should not raise


def test_value_event_call_lambda_observers_in_order():
    event = ValueEvent[str]()
    call_order = []

    event.observe(lambda value: call_order.append("first"))
    event.observe(lambda value: call_order.append("second"))
    event.observe(lambda value: call_order.append("third"))

    event("test")

    assert call_order == ["first", "second", "third"]


def test_value_event_call_mock_observer_with_none_value():
    event = ValueEvent[str | None]()
    observer = OneParameterObserver()

    event.observe(observer)
    event(None)

    observer.assert_called_once_with(None)


def test_value_event_observe_no_parameters_mock_observer():
    event = ValueEvent[str]()
    observer = NoParametersObserver()

    event.observe(observer)
    event("test_value")

    observer.assert_called_once_with()


def test_value_event_observe_one_parameter_mock_observer():
    event = ValueEvent[str]()
    observer = OneParameterObserver()

    event.observe(observer)
    event("test_value")

    observer.assert_called_once_with("test_value")


def test_value_event_observe_one_default_parameter_mock_observer():
    event = ValueEvent[str]()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event("test_value")

    observer.assert_called_once_with("test_value")


def test_value_event_observe_one_required_one_default_parameter_mock_observer():
    event = ValueEvent[str]()
    observer = OneRequiredOneDefaultParameterObserver()

    event.observe(observer)
    event("test_value")

    observer.assert_called_once_with("test_value", "default")


def test_value_event_unobserve_mock_observer():
    event = ValueEvent[int]()
    observer = OneParameterObserver()

    event.observe(observer)
    event.unobserve(observer)
    event(42)

    observer.assert_not_called()


def test_value_event_call_multiple_mock_observers():
    event = ValueEvent[str]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()

    event.observe(observer0)
    event.observe(observer1)
    event("hello")

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")


def test_value_event_observe_function_observer_too_many_parameters_fails():
    event = ValueEvent[str]()

    def bad_observer(param0, param1):
        pass

    with pytest.raises(ValueError):
        event.observe(bad_observer)


def test_value_event_observe_lambda_no_parameters():
    event = ValueEvent[str]()
    called = []

    event.observe(lambda: called.append(True))
    event("test_value")

    assert called == [True]


def test_value_event_observe_lambda_one_parameter():
    event = ValueEvent[str]()
    received_values = []

    event.observe(lambda value0: received_values.append(value0))
    event("test_value")

    assert received_values == ["test_value"]


def test_value_event_observe_lambda_one_default_parameter():
    event = ValueEvent[str]()
    received_values = []

    event.observe(lambda value0="default": received_values.append(value0))
    event("test_value")

    assert received_values == ["test_value"]


def test_value_event_unobserve_lambda_observer():
    event = ValueEvent[int]()
    called = []
    observer = lambda value0: called.append(value0)

    event.observe(observer)
    event.unobserve(observer)
    event(42)

    assert called == []


def test_value_event_observe_lambda_observer_too_many_parameters_fails():
    event = ValueEvent[str]()

    with pytest.raises(ValueError, match="has too many non-default parameters: 2 > 1"):
        event.observe(lambda param0, param1: None)


def test_value_event_call_with_two_parameters_fails():
    event = ValueEvent[str]()

    with pytest.raises(TypeError):
        event("param0", "param1")


def test_value_event_observe_mock_observer_times_parameter_limits_calls():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.observe(mock_observer, times=2)

    event("test")
    event("test")
    event("test")

    assert mock_observer.call_count == 2


def test_value_event_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.observe(mock_observer, times=1)
    event("test")

    assert not event.is_observed(mock_observer)


def test_value_event_observe_mock_observer_times_none_unlimited_calls():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.observe(mock_observer, times=None)

    for _ in range(10):
        event("test")

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
