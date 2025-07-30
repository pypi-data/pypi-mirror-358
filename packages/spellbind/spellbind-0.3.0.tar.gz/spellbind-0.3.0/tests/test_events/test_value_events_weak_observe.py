import gc

import pytest

from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver, TwoParametersObserver
from spellbind.event import ValueEvent


def test_value_event_weak_observe_mock_observer_adds_subscription():
    event = ValueEvent[str]()
    observer = OneParameterObserver()

    event.weak_observe(observer)

    assert event.is_observed(observer)


def test_value_event_weak_observe_mock_observer_too_many_parameters_fails():
    event = ValueEvent[str]()

    with pytest.raises(ValueError):
        event.weak_observe(TwoParametersObserver())


def test_value_event_weak_observe_no_parameters_mock_observer_called():
    event = ValueEvent[str]()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event("test_value")

    observer.assert_called_once_with()


def test_value_event_weak_observe_one_parameter_mock_observer_called():
    event = ValueEvent[str]()
    observer = OneParameterObserver()
    event.weak_observe(observer)

    event("test_value")

    observer.assert_called_once_with("test_value")


def test_value_event_weak_observe_one_default_parameter_mock_observer_called():
    event = ValueEvent[str]()
    observer = OneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value")

    observer.assert_called_once_with("test_value")


def test_value_event_weak_observe_one_required_one_default_parameter_mock_observer_called():
    event = ValueEvent[str]()
    observer = OneRequiredOneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value")

    observer.assert_called_once_with("test_value", "default")


def test_value_event_weak_observe_unobserve_mock_observer_removes_subscription():
    event = ValueEvent[str]()
    observer = OneParameterObserver()
    event.weak_observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_value_event_weak_observe_unobserve_twice_mock_observer_removes_subscription():
    event = ValueEvent[str]()
    observer = OneParameterObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)
    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_value_event_weak_observe_twice_unobserve_once_mock_observer_still_subscribed():
    event = ValueEvent[str]()
    observer = OneParameterObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)

    assert event.is_observed(observer)


def test_value_event_weak_observe_mock_observer_auto_cleanup():
    event = ValueEvent[str]()
    observer = OneParameterObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value")

    assert len(event._subscriptions) == 0


def test_value_event_weak_observe_function_observer():
    event = ValueEvent[str]()
    calls = []

    def observer(value):
        calls.append(value)

    event.weak_observe(observer)
    event("test_value")

    assert calls == ["test_value"]


def test_value_event_weak_observe_function_observer_no_parameters():
    event = ValueEvent[str]()
    calls = []

    def observer():
        calls.append(True)

    event.weak_observe(observer)
    event("test_value")

    assert calls == [True]


def test_value_event_mixed_weak_strong_mock_observers():
    event = ValueEvent[str]()
    strong_observer = OneParameterObserver()
    weak_observer = OneParameterObserver()

    event.observe(strong_observer)
    event.weak_observe(weak_observer)

    event("test_value")

    strong_observer.assert_called_once_with("test_value")
    weak_observer.assert_called_once_with("test_value")


def test_value_event_weak_observe_mock_observer_method_auto_cleanup():
    event = ValueEvent[str]()

    observer = OneParameterObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value")

    assert len(event._subscriptions) == 0


def test_value_event_weak_observe_mock_observer_method_before_cleanup():
    event = ValueEvent[str]()

    observer = OneParameterObserver()
    event.weak_observe(observer)

    event("test_value")

    observer.assert_called_once_with("test_value")
    assert len(event._subscriptions) == 1


def test_value_event_weak_observe_lambda_observer_cleaned_immediately():
    event = ValueEvent[str]()
    calls = []

    event.weak_observe(lambda value: calls.append(value))
    event("test_value")

    assert calls == []


def test_value_event_weak_observe_lambda_observer_no_parameters_cleaned_immediately():
    event = ValueEvent[str]()
    calls = []

    event.weak_observe(lambda: calls.append(True))
    event("test_value")

    assert calls == []


def test_value_event_weak_observe_lambda_observer_cleanup():
    event = ValueEvent[str]()
    calls = []

    observer = lambda value: calls.append(value)
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value")

    assert len(event._subscriptions) == 0
    assert calls == []


def test_value_event_weak_observe_unobserve_lambda_observer():
    event = ValueEvent[str]()
    calls = []

    observer = lambda value: calls.append(value)
    event.weak_observe(observer)
    event.unobserve(observer)

    event("test_value")

    assert calls == []
    assert not event.is_observed(observer)


def test_value_event_call_mixed_weak_strong_lambda_observers_in_order():
    event = ValueEvent[str]()
    calls = []

    observer0 = lambda value: calls.append(("test0", value))
    observer1 = lambda value: calls.append(("test1", value))
    observer2 = lambda value: calls.append(("test2", value))
    observer3 = lambda value: calls.append(("test3", value))

    event.observe(observer0)
    event.weak_observe(observer1)
    event.observe(observer2)
    event.weak_observe(observer3)

    event("test")

    assert calls == [("test0", "test"), ("test1", "test"), ("test2", "test"), ("test3", "test")]


def test_value_event_weak_observe_mock_observer_with_none_value():
    event = ValueEvent[str | None]()
    observer = OneParameterObserver()

    event.weak_observe(observer)
    event(None)

    observer.assert_called_once_with(None)


def test_value_event_weak_observe_lambda_observer_with_default_parameter():
    event = ValueEvent[str]()
    calls = []

    observer = lambda value="default": calls.append(value)
    event.weak_observe(observer)
    event("test_value")

    assert calls == ["test_value"]


def test_value_event_weak_observe_multiple_mock_observers_different_parameters():
    event = ValueEvent[str]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()
    observer2 = OneDefaultParameterObserver()

    event.weak_observe(observer0)
    event.weak_observe(observer1)
    event.weak_observe(observer2)
    event("hello")

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")
    observer2.assert_called_once_with("hello")


def test_value_event_weak_observe_mock_observer_times_parameter_limits_calls():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.weak_observe(mock_observer, times=2)

    event("test")
    event("test")
    event("test")

    assert mock_observer.call_count == 2


def test_value_event_weak_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.weak_observe(mock_observer, times=1)
    event("test")

    assert not event.is_observed(mock_observer)


def test_value_event_weak_observe_mock_observer_times_none_unlimited_calls():
    event = ValueEvent[str]()
    mock_observer = OneParameterObserver()

    event.weak_observe(mock_observer, times=None)

    for _ in range(10):
        event("test")

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
