import gc

import pytest

from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver, TwoParametersObserver, TwoDefaultParametersObserver, \
    ThreeParametersObserver
from spellbind.event import BiEvent


def test_bi_event_weak_observe_mock_observer_adds_subscription():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    event.weak_observe(observer)

    assert event.is_observed(observer)


def test_bi_event_weak_observe_mock_observer_too_many_parameters_fails():
    event = BiEvent[str, int]()

    with pytest.raises(ValueError):
        event.weak_observe(ThreeParametersObserver())


def test_bi_event_weak_observe_no_parameters_mock_observer_called():
    event = BiEvent[str, int]()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with()


def test_bi_event_weak_observe_one_parameter_mock_observer_called():
    event = BiEvent[str, int]()
    observer = OneParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value")


def test_bi_event_weak_observe_one_default_parameter_mock_observer_called():
    event = BiEvent[str, int]()
    observer = OneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value")


def test_bi_event_weak_observe_one_required_one_default_parameter_mock_observer_called():
    event = BiEvent[str, int]()
    observer = OneRequiredOneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_weak_observe_two_parameters_mock_observer_called():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_weak_observe_two_default_parameters_mock_observer_called():
    event = BiEvent[str, int]()
    observer = TwoDefaultParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_weak_observe_unobserve_mock_observer_removes_subscription():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_bi_event_weak_observe_unobserve_twice_mock_observer_removes_subscription():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)
    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_bi_event_weak_observe_twice_unobserve_once_mock_observer_still_subscribed():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)

    assert event.is_observed(observer)


def test_bi_event_weak_observe_mock_observer_auto_cleanup():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42)

    assert len(event._subscriptions) == 0


def test_bi_event_weak_observe_function_observer():
    event = BiEvent[str, int]()
    calls = []

    def observer(value0, value1):
        calls.append((value0, value1))

    event.weak_observe(observer)
    event("test_value", 42)

    assert calls == [("test_value", 42)]


def test_bi_event_weak_observe_function_observer_one_parameter():
    event = BiEvent[str, int]()
    calls = []

    def observer(value0):
        calls.append(value0)

    event.weak_observe(observer)
    event("test_value", 42)

    assert calls == ["test_value"]


def test_bi_event_weak_observe_function_observer_no_parameters():
    event = BiEvent[str, int]()
    calls = []

    def observer():
        calls.append(True)

    event.weak_observe(observer)
    event("test_value", 42)

    assert calls == [True]


def test_bi_event_mixed_weak_strong_mock_observers():
    event = BiEvent[str, int]()
    strong_observer = TwoParametersObserver()
    weak_observer = TwoParametersObserver()

    event.observe(strong_observer)
    event.weak_observe(weak_observer)

    event("test_value", 42)

    strong_observer.assert_called_once_with("test_value", 42)
    weak_observer.assert_called_once_with("test_value", 42)


def test_bi_event_weak_observe_mock_observer_method_auto_cleanup():
    event = BiEvent[str, int]()

    observer = TwoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42)

    assert len(event._subscriptions) == 0


def test_bi_event_weak_observe_mock_observer_method_before_cleanup():
    event = BiEvent[str, int]()

    observer = TwoParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)
    assert len(event._subscriptions) == 1


def test_bi_event_weak_observe_lambda_observer_cleaned_immediately():
    event = BiEvent[str, int]()
    calls = []

    event.weak_observe(lambda value0, value1: calls.append((value0, value1)))
    event("test_value", 42)

    assert calls == []


def test_bi_event_weak_observe_lambda_observer_one_parameter_cleaned_immediately():
    event = BiEvent[str, int]()
    calls = []

    event.weak_observe(lambda value0: calls.append(value0))
    event("test_value", 42)

    assert calls == []


def test_bi_event_weak_observe_lambda_observer_no_parameters_cleaned_immediately():
    event = BiEvent[str, int]()
    calls = []

    event.weak_observe(lambda: calls.append(True))
    event("test_value", 42)

    assert calls == []


def test_bi_event_weak_observe_lambda_observer_cleanup():
    event = BiEvent[str, int]()
    calls = []

    observer = lambda value0, value1: calls.append((value0, value1))
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42)

    assert len(event._subscriptions) == 0
    assert calls == []


def test_bi_event_weak_observe_unobserve_lambda_observer():
    event = BiEvent[str, int]()
    calls = []

    observer = lambda value0, value1: calls.append((value0, value1))
    event.weak_observe(observer)
    event.unobserve(observer)

    event("test_value", 42)

    assert calls == []
    assert not event.is_observed(observer)


def test_bi_event_call_mixed_weak_strong_lambda_observers_in_order():
    event = BiEvent[str, int]()
    calls = []

    observer0 = lambda value0, value1: calls.append(("test0", value0, value1))
    observer1 = lambda value0, value1: calls.append(("test1", value0, value1))
    observer2 = lambda value0, value1: calls.append(("test2", value0, value1))
    observer3 = lambda value0, value1: calls.append(("test3", value0, value1))

    event.observe(observer0)
    event.weak_observe(observer1)
    event.observe(observer2)
    event.weak_observe(observer3)

    event("test", 123)

    assert calls == [("test0", "test", 123), ("test1", "test", 123), ("test2", "test", 123), ("test3", "test", 123)]


def test_bi_event_weak_observe_mock_observer_with_none_values():
    event = BiEvent[str | None, int | None]()
    observer = TwoParametersObserver()

    event.weak_observe(observer)
    event(None, None)

    observer.assert_called_once_with(None, None)


def test_bi_event_weak_observe_same_mock_observer_multiple_times():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    event.weak_observe(observer)
    event.weak_observe(observer)
    event("test", 42)

    assert observer.call_count == 2


def test_bi_event_weak_observe_lambda_observer_with_default_parameters():
    event = BiEvent[str, int]()
    calls = []

    observer = lambda value0="default0", value1=0: calls.append((value0, value1))
    event.weak_observe(observer)
    event("test_value", 42)

    assert calls == [("test_value", 42)]


def test_bi_event_weak_observe_multiple_mock_observers_different_parameters():
    event = BiEvent[str, int]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()
    observer2 = TwoParametersObserver()
    observer3 = OneRequiredOneDefaultParameterObserver()

    event.weak_observe(observer0)
    event.weak_observe(observer1)
    event.weak_observe(observer2)
    event.weak_observe(observer3)
    event("hello", 123)

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")
    observer2.assert_called_once_with("hello", 123)
    observer3.assert_called_once_with("hello", 123)


def test_bi_event_weak_observe_mock_observer_times_parameter_limits_calls():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.weak_observe(mock_observer, times=2)

    event("test", 42)
    event("test", 42)
    event("test", 42)

    assert mock_observer.call_count == 2


def test_bi_event_weak_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.weak_observe(mock_observer, times=1)
    event("test", 42)

    assert not event.is_observed(mock_observer)


def test_bi_event_weak_observe_mock_observer_times_none_unlimited_calls():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.weak_observe(mock_observer, times=None)

    for _ in range(10):
        event("test", 42)

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
