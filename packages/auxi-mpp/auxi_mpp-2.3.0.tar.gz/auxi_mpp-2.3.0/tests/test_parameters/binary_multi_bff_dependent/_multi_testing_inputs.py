from collections.abc import Callable

from ..binary_multi._multi_testing_inputs import (
    activity_error_test_inputs,
    activity_tests,
    multi_error_test_inputs,
    multi_testing_inputs,
)
from ._dummy_bff import dummy_bff


# positive test temperature and composition tests
multi_testing_inputs_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in multi_testing_inputs:
    tup_bff = (*tup, dummy_bff)
    multi_testing_inputs_bff.append(tup_bff)

# reuse original name
multi_testing_inputs = multi_testing_inputs_bff


# tests that should fail
multi_error_test_inputs_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in multi_error_test_inputs:
    tup_bff = (*tup, dummy_bff)
    multi_error_test_inputs_bff.append(tup_bff)

# reuse original name
multi_error_test_inputs = multi_error_test_inputs_bff

# test activity inputs
activity_tests_bff: list[
    tuple[
        float,
        dict[str, float],
        dict[str, dict[str, float]],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in activity_tests:
    tup_bff = (*tup, dummy_bff)
    activity_tests_bff.append(tup_bff)

# reuse original name
activity_tests = activity_tests_bff

# activity error tests
activity_error_test_inputs_bff: list[
    tuple[
        float,
        dict[str, float],
        dict[str, dict[str, float]],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in activity_error_test_inputs:
    tup_bff = (*tup, dummy_bff)
    activity_error_test_inputs_bff.append(tup_bff)

# reuse original name
activity_error_test_inputs = activity_error_test_inputs_bff

# temperature limits for binary vs multi
temperature_limits_binary_vs_multi = [(1000, {"SiO2": 0.5, "Al2O3": 0.5}), (2500, {"SiO2": 0.5, "CaO": 0.5})]
