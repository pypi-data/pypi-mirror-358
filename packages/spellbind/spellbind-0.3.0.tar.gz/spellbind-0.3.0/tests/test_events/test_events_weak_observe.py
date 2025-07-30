import gc

import pytest

from conftest import NoParametersObserver, OneParameterObserver
from spellbind.event import Event


def test_event_weak_observe_mock_observer_adds_subscription():
    event = Event()
    observer = NoParametersObserver()

    event.weak_observe(observer)

    assert event.is_observed(observer)


def test_event_weak_observe_mock_observer_too_many_parameters_fails():
    event = Event()

    with pytest.raises(ValueError):
        event.weak_observe(OneParameterObserver())


def test_event_weak_observe_mock_observer_called():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event()

    observer.assert_called_once_with()


def test_event_weak_observe_unobserve_mock_observer_removes_subscription():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_event_weak_observe_unobserve_twice_mock_observer_removes_subscription():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)
    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_event_weak_observe_twice_unobserve_once_mock_observer_still_subscribed():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)

    assert event.is_observed(observer)


def test_event_weak_observe_mock_observer_auto_cleanup():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0


def test_event_weak_observe_function_observer():
    event = Event()
    calls = []

    def observer():
        calls.append(True)

    event.weak_observe(observer)
    event()

    assert calls == [True]


def test_event_mixed_weak_strong_mock_observers():
    event = Event()
    strong_observer = NoParametersObserver()
    weak_observer = NoParametersObserver()

    event.observe(strong_observer)
    event.weak_observe(weak_observer)

    event()

    strong_observer.assert_called_once_with()
    weak_observer.assert_called_once_with()


def test_event_weak_observe_mock_observer_method_auto_cleanup():
    event = Event()

    observer = NoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0


def test_event_weak_observe_mock_observer_method_before_cleanup():
    event = Event()

    observer = NoParametersObserver()
    event.weak_observe(observer)

    event()

    observer.assert_called_once_with()
    assert len(event._subscriptions) == 1


def test_event_weak_observe_lambda_observer_cleaned_immediately():
    event = Event()
    calls = []

    event.weak_observe(lambda: calls.append(True))
    event()

    assert calls == []


def test_event_weak_observe_lambda_observer_cleanup():
    event = Event()
    calls = []

    observer = lambda: calls.append(True)
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0
    assert calls == []


def test_event_weak_observe_unobserve_lambda_observer():
    event = Event()
    calls = []

    observer = lambda: calls.append(True)
    event.weak_observe(observer)
    event.unobserve(observer)

    event()

    assert calls == []
    assert not event.is_observed(observer)


def test_event_call_mixed_weak_strong_lambda_observers_in_order():
    event = Event()
    calls = []

    observer0 = lambda: calls.append("test 0")
    observer1 = lambda: calls.append("test 1")
    observer2 = lambda: calls.append("test 2")
    observer3 = lambda: calls.append("test 3")

    event.observe(observer0)
    event.weak_observe(observer1)
    event.observe(observer2)
    event.weak_observe(observer3)

    event()

    assert calls == ["test 0", "test 1", "test 2", "test 3"]


def test_event_weak_observe_mock_observer_times_parameter_limits_calls():
    event = Event()
    mock_observer = NoParametersObserver()

    event.weak_observe(mock_observer, times=2)

    event()
    event()
    event()

    assert mock_observer.call_count == 2


def test_event_weak_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = Event()
    mock_observer = NoParametersObserver()

    event.weak_observe(mock_observer, times=1)
    event()

    assert not event.is_observed(mock_observer)


def test_event_weak_observe_mock_observer_times_none_unlimited_calls():
    event = Event()
    mock_observer = NoParametersObserver()

    event.weak_observe(mock_observer, times=None)

    for _ in range(10):
        event()

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
