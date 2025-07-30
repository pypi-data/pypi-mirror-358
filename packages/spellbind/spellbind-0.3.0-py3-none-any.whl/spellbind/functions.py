import inspect
from inspect import Parameter
from typing import Callable, Iterable


def _is_positional_parameter(param: Parameter) -> bool:
    return param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)


def count_positional_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for parameter in parameters.values() if _is_positional_parameter(parameter))


def _is_required_positional_parameter(param: Parameter) -> bool:
    return param.default == param.empty and _is_positional_parameter(param)


def count_non_default_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for param in parameters.values() if _is_required_positional_parameter(param))


def assert_parameter_max_count(callable_: Callable, max_count: int) -> None:
    if count_non_default_parameters(callable_) > max_count:
        if hasattr(callable_, '__name__'):
            callable_name = callable_.__name__
        elif hasattr(callable_, '__class__'):
            callable_name = callable_.__class__.__name__
        else:
            callable_name = str(callable_)  # pragma: no cover
        raise ValueError(f"Callable {callable_name} has too many non-default parameters: "
                         f"{count_non_default_parameters(callable_)} > {max_count}")


def _multiply_all_ints(vals: Iterable[int]) -> int:
    result = 1
    for val in vals:
        result *= val
    return result


def _multiply_all_floats(vals: Iterable[float]) -> float:
    result = 1.
    for val in vals:
        result *= val
    return result


def _clamp_int(value: int, min_value: int, max_value: int) -> int:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value


def _clamp_float(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value
