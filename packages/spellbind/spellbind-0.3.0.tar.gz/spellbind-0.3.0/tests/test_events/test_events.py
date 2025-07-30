import pytest

from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver
from spellbind.event import Event


def test_event_initialization_empty_subscriptions():
    event = Event()
    assert event._subscriptions == []


def test_event_observe_mock_observer_adds_subscription():
    event = Event()
    observer = NoParametersObserver()

    event.observe(observer)

    assert event.is_observed(observer)


def test_event_observe_mock_observer_too_many_parameters_fails():
    event = Event()

    with pytest.raises(ValueError):
        event.observe(OneParameterObserver())


def test_event_unobserve_mock_observer_removes_subscription():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_event_unobserve_nonexistent_mock_observer_fails():
    event = Event()

    with pytest.raises(ValueError):
        event.unobserve(NoParametersObserver())


def test_event_call_unobserved_mock_observer_not_invoked():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)
    event.unobserve(observer)

    event()

    observer.assert_not_called()


def test_event_call_invokes_all_mock_observers():
    event = Event()
    observer0 = NoParametersObserver()
    observer1 = NoParametersObserver()
    event.observe(observer0)
    event.observe(observer1)

    event()

    observer0.assert_called_once_with()
    observer1.assert_called_once_with()


def test_event_observe_mock_observer_with_default_parameter():
    event = Event()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event()

    observer.assert_called_once_with("default")


def test_event_call_with_no_observers():
    event = Event()
    event()


def test_event_observe_function_observer_with_default_parameter():
    event = Event()

    calls = []

    def observer_with_default(param="default"):
        calls.append(param)

    event.observe(observer_with_default)
    event()
    assert calls == ["default"]


def test_event_observe_lambda_observer():
    event = Event()
    calls = []

    event.observe(lambda: calls.append(True))
    event()

    assert calls == [True]


def test_event_observe_lambda_observer_with_one_parameter_fails():
    event = Event()
    calls = []

    with pytest.raises(ValueError):
        event.observe(lambda x: calls.append(True))


def test_event_observe_mock_observer_times_parameter_limits_calls():
    event = Event()
    mock_observer = NoParametersObserver()

    event.observe(mock_observer, times=2)

    event()
    event()
    event()

    assert mock_observer.call_count == 2


def test_event_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = Event()
    mock_observer = NoParametersObserver()

    event.observe(mock_observer, times=1)
    event()

    assert not event.is_observed(mock_observer)


def test_event_observe_mock_observer_times_none_unlimited_calls():
    event = Event()
    mock_observer = NoParametersObserver()

    event.observe(mock_observer, times=None)

    for _ in range(10):
        event()

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
