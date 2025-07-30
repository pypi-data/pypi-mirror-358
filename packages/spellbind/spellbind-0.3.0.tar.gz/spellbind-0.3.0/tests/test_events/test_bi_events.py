import pytest
from spellbind.event import BiEvent
from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver, TwoParametersObserver, TwoDefaultParametersObserver


def test_bi_event_observe_no_parameters_mock_observer():
    event = BiEvent[str, int]()
    observer = NoParametersObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with()


def test_bi_event_observe_one_parameter_mock_observer():
    event = BiEvent[str, int]()
    observer = OneParameterObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with("test_value")


def test_bi_event_observe_one_default_parameter_mock_observer():
    event = BiEvent[str, int]()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with("test_value")


def test_bi_event_observe_one_required_one_default_parameter_mock_observer():
    event = BiEvent[str, int]()
    observer = OneRequiredOneDefaultParameterObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_observe_two_parameters_mock_observer():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_observe_two_default_parameters_mock_observer():
    event = BiEvent[str, int]()
    observer = TwoDefaultParametersObserver()

    event.observe(observer)
    event("test_value", 42)

    observer.assert_called_once_with("test_value", 42)


def test_bi_event_unobserve_mock_observer():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    event.observe(observer)
    event.unobserve(observer)
    event("test", 42)

    observer.assert_not_called()


def test_bi_event_call_multiple_mock_observers():
    event = BiEvent[str, int]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()
    observer2 = TwoParametersObserver()

    event.observe(observer0)
    event.observe(observer1)
    event.observe(observer2)
    event("hello", 123)

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")
    observer2.assert_called_once_with("hello", 123)


def test_bi_event_observe_function_observer_too_many_parameters_fails():
    event = BiEvent[str, int]()

    def bad_observer(param0, param1, param2):
        pass

    with pytest.raises(ValueError):
        event.observe(bad_observer)


def test_bi_event_observe_lambda_no_parameters():
    event = BiEvent[str, int]()
    called = []

    event.observe(lambda: called.append(True))
    event("test_value", 42)

    assert called == [True]


def test_bi_event_observe_lambda_one_parameter():
    event = BiEvent[str, int]()
    calls = []

    event.observe(lambda value0: calls.append(value0))
    event("test_value", 42)

    assert calls == ["test_value"]


def test_bi_event_observe_lambda_two_parameters():
    event = BiEvent[str, int]()
    calls = []

    event.observe(lambda value0, value1: calls.append((value0, value1)))
    event("test_value", 42)

    assert calls == [("test_value", 42)]


def test_bi_event_unobserve_lambda_observer():
    event = BiEvent[str, int]()
    calls = []
    observer = lambda value0, value1: calls.append((value0, value1))

    event.observe(observer)
    event("test0", 0)
    event.unobserve(observer)
    event("test1", 1)

    assert calls == [("test0", 0)]


def test_bi_event_observe_lambda_observer_too_many_parameters_fails():
    event = BiEvent[str, int]()

    with pytest.raises(ValueError):
        event.observe(lambda param0, param1, param2: None)


def test_bi_event_call_with_one_parameter_fails():
    event = BiEvent[str, int]()

    with pytest.raises(TypeError):
        event("param0")


def test_bi_event_call_with_three_parameters_fails():
    event = BiEvent[str, int]()

    with pytest.raises(TypeError):
        event("param0", 42, "param2")


def test_bi_event_unobserve_nonexistent_mock_observer_fails():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    with pytest.raises(ValueError):
        event.unobserve(observer)


def test_bi_event_observe_same_mock_observer_multiple_times():
    event = BiEvent[str, int]()
    observer = TwoParametersObserver()

    event.observe(observer)
    event.observe(observer)
    event("test", 42)

    assert observer.call_count == 2
    observer.assert_called_with("test", 42)


def test_bi_event_call_with_no_observers():
    event = BiEvent[str, int]()
    event("test_value", 42)  # Should not raise


def test_bi_event_call_lambda_observers_in_order():
    event = BiEvent[str, int]()
    call_order = []

    event.observe(lambda value0, value1: call_order.append("first"))
    event.observe(lambda value0, value1: call_order.append("second"))
    event.observe(lambda value0, value1: call_order.append("third"))

    event("test", 42)

    assert call_order == ["first", "second", "third"]


def test_bi_event_call_mock_observer_with_none_values():
    event = BiEvent[str | None, int | None]()
    observer = TwoParametersObserver()

    event.observe(observer)
    event(None, None)

    observer.assert_called_once_with(None, None)


def test_bi_event_observe_mock_observer_times_parameter_limits_calls():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.observe(mock_observer, times=2)

    event("test", 42)
    event("test", 42)
    event("test", 42)

    assert mock_observer.call_count == 2


def test_bi_event_observe_mock_observer_times_parameter_removes_subscription_after_limit():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.observe(mock_observer, times=1)
    event("test", 42)

    assert not event.is_observed(mock_observer)


def test_bi_event_observe_mock_observer_times_none_unlimited_calls():
    event = BiEvent[str, int]()
    mock_observer = TwoParametersObserver()

    event.observe(mock_observer, times=None)

    for _ in range(10):
        event("test", 42)

    assert mock_observer.call_count == 10
    assert event.is_observed(mock_observer)
