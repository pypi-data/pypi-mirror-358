import gc

import pytest

from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver, TwoParametersObserver, \
    ThreeParametersObserver, ThreeDefaultParametersObserver, TwoRequiredOneDefaultParameterObserver
from spellbind.event import TriEvent


def test_tri_event_weak_observe_mock_observer_adds_subscription():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    event.weak_observe(observer)

    assert event.is_observed(observer)


def test_tri_event_weak_observe_mock_observer_too_many_parameters_fails():
    event = TriEvent[str, int, bool]()

    def bad_observer(param0, param1, param2, param3):
        pass

    with pytest.raises(ValueError):
        event.weak_observe(bad_observer)


def test_tri_event_weak_observe_no_parameters_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with()


def test_tri_event_weak_observe_one_parameter_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = OneParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value")


def test_tri_event_weak_observe_one_default_parameter_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = OneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value")


def test_tri_event_weak_observe_one_required_one_default_parameter_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = OneRequiredOneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42)


def test_tri_event_weak_observe_two_parameters_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = TwoParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42)


def test_tri_event_weak_observe_two_required_one_default_parameter_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = TwoRequiredOneDefaultParameterObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42, True)


def test_tri_event_weak_observe_three_parameters_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42, True)


def test_tri_event_weak_observe_three_default_parameters_mock_observer_called():
    event = TriEvent[str, int, bool]()
    observer = ThreeDefaultParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with(param0="test_value", param1=42, param2=True)


def test_tri_event_weak_observe_unobserve_mock_observer_removes_subscription():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()
    event.weak_observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_tri_event_weak_observe_unobserve_twice_mock_observer_removes_subscription():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)
    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_tri_event_weak_observe_twice_unobserve_once_mock_observer_still_subscribed():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)

    assert event.is_observed(observer)


def test_tri_event_weak_observe_mock_observer_auto_cleanup():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42, True)

    assert len(event._subscriptions) == 0


def test_tri_event_weak_observe_function_observer():
    event = TriEvent[str, int, bool]()
    calls = []

    def observer(value0, value1, value2):
        calls.append((value0, value1, value2))

    event.weak_observe(observer)
    event("test_value", 42, True)

    assert calls == [("test_value", 42, True)]


def test_tri_event_weak_observe_function_observer_two_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    def observer(value0, value1):
        calls.append((value0, value1))

    event.weak_observe(observer)
    event("test_value", 42, True)

    assert calls == [("test_value", 42)]


def test_tri_event_weak_observe_function_observer_one_parameter():
    event = TriEvent[str, int, bool]()
    calls = []

    def observer(value0):
        calls.append(value0)

    event.weak_observe(observer)
    event("test_value", 42, True)

    assert calls == ["test_value"]


def test_tri_event_weak_observe_function_observer_no_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    def observer():
        calls.append(True)

    event.weak_observe(observer)
    event("test_value", 42, True)

    assert calls == [True]


def test_tri_event_mixed_weak_strong_mock_observers():
    event = TriEvent[str, int, bool]()
    strong_observer = ThreeParametersObserver()
    weak_observer = ThreeParametersObserver()

    event.observe(strong_observer)
    event.weak_observe(weak_observer)

    event("test_value", 42, True)

    strong_observer.assert_called_once_with("test_value", 42, True)
    weak_observer.assert_called_once_with("test_value", 42, True)


def test_tri_event_weak_observe_mock_observer_method_auto_cleanup():
    event = TriEvent[str, int, bool]()

    observer = ThreeParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42, True)

    assert len(event._subscriptions) == 0


def test_tri_event_weak_observe_mock_observer_method_before_cleanup():
    event = TriEvent[str, int, bool]()

    observer = ThreeParametersObserver()
    event.weak_observe(observer)

    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42, True)
    assert len(event._subscriptions) == 1


def test_tri_event_weak_observe_lambda_observer_cleaned_immediately():
    event = TriEvent[str, int, bool]()
    calls = []

    event.weak_observe(lambda value0, value1, value2: calls.append((value0, value1, value2)))
    event("test_value", 42, True)

    assert calls == []


def test_tri_event_weak_observe_lambda_observer_two_parameters_cleaned_immediately():
    event = TriEvent[str, int, bool]()
    calls = []

    event.weak_observe(lambda value0, value1: calls.append((value0, value1)))
    event("test_value", 42, True)

    assert calls == []


def test_tri_event_weak_observe_lambda_observer_one_parameter_cleaned_immediately():
    event = TriEvent[str, int, bool]()
    calls = []

    event.weak_observe(lambda value0: calls.append(value0))
    event("test_value", 42, True)

    assert calls == []


def test_tri_event_weak_observe_lambda_observer_no_parameters_cleaned_immediately():
    event = TriEvent[str, int, bool]()
    calls = []

    event.weak_observe(lambda: calls.append(True))
    event("test_value", 42, True)

    assert calls == []


def test_tri_event_weak_observe_lambda_observer_cleanup():
    event = TriEvent[str, int, bool]()
    calls = []

    observer = lambda value0, value1, value2: calls.append((value0, value1, value2))
    event.weak_observe(observer)

    del observer
    gc.collect()

    event("test_value", 42, True)

    assert len(event._subscriptions) == 0
    assert calls == []


def test_tri_event_weak_observe_unobserve_lambda_observer():
    event = TriEvent[str, int, bool]()
    calls = []

    observer = lambda value0, value1, value2: calls.append((value0, value1, value2))
    event.weak_observe(observer)
    event.unobserve(observer)

    event("test_value", 42, True)

    assert calls == []
    assert not event.is_observed(observer)


def test_tri_event_call_mixed_weak_strong_lambda_observers_in_order():
    event = TriEvent[str, int, bool]()
    calls = []

    observer0 = lambda value0, value1, value2: calls.append(("test0", value0, value1, value2))
    observer1 = lambda value0, value1, value2: calls.append(("test1", value0, value1, value2))
    observer2 = lambda value0, value1, value2: calls.append(("test2", value0, value1, value2))
    observer3 = lambda value0, value1, value2: calls.append(("test3", value0, value1, value2))

    event.observe(observer0)
    event.weak_observe(observer1)
    event.observe(observer2)
    event.weak_observe(observer3)

    event("test", 123, False)

    assert calls == [("test0", "test", 123, False), ("test1", "test", 123, False), ("test2", "test", 123, False), ("test3", "test", 123, False)]


def test_tri_event_weak_observe_mock_observer_with_none_values():
    event = TriEvent[str | None, int | None, bool | None]()
    observer = ThreeParametersObserver()

    event.weak_observe(observer)
    event(None, None, None)

    observer.assert_called_once_with(None, None, None)


def test_tri_event_weak_observe_same_mock_observer_multiple_times():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    event.weak_observe(observer)
    event.weak_observe(observer)
    event("test", 42, True)

    assert observer.call_count == 2


def test_tri_event_weak_observe_lambda_observer_with_default_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    observer = lambda value0="default0", value1=0, value2=False: calls.append((value0, value1, value2))
    event.weak_observe(observer)
    event("test_value", 42, True)

    assert calls == [("test_value", 42, True)]


def test_tri_event_weak_observe_multiple_mock_observers_different_parameters():
    event = TriEvent[str, int, bool]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()
    observer2 = TwoParametersObserver()
    observer3 = ThreeParametersObserver()
    observer4 = TwoRequiredOneDefaultParameterObserver()

    event.weak_observe(observer0)
    event.weak_observe(observer1)
    event.weak_observe(observer2)
    event.weak_observe(observer3)
    event.weak_observe(observer4)
    event("hello", 123, False)

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")
    observer2.assert_called_once_with("hello", 123)
    observer3.assert_called_once_with("hello", 123, False)
    observer4.assert_called_once_with("hello", 123, False)


def test_tri_event_weak_observe_mock_observer_times_parameter_limits_calls():
    event = TriEvent[str, int, bool]()
    mock_observer = ThreeParametersObserver()

    event.weak_observe(mock_observer, times=2)

    event("test", 42, True)
    event("test", 42, True)
    event("test", 42, True)

    assert mock_observer.call_count == 2


def test_tri_event_weak_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = TriEvent[str, int, bool]()
    mock_observer = ThreeParametersObserver()

    event.weak_observe(mock_observer, times=1)
    event("test", 42, True)

    assert not event.is_observed(mock_observer)


def test_tri_event_weak_observe_mock_observer_times_none_unlimited_calls():
    event = TriEvent[str, int, bool]()
    mock_observer = ThreeParametersObserver()

    event.weak_observe(mock_observer, times=None)

    for _ in range(10):
        event("test", 42, True)

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
