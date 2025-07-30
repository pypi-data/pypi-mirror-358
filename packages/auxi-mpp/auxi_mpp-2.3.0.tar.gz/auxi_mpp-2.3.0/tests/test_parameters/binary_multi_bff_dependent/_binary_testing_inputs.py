from collections.abc import Callable

from ..binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)
from ._dummy_bff import dummy_bff


# normal tests
binary_testing_inputs_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in binary_testing_inputs:
    tup_bff = (*tup, dummy_bff)
    binary_testing_inputs_bff.append(tup_bff)

# reuse original name
binary_testing_inputs = binary_testing_inputs_bff

# error tests
binary_error_test_inputs_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in binary_error_test_inputs:
    tup_bff = (*tup, dummy_bff)
    binary_error_test_inputs_bff.append(tup_bff)

# reuse original name
binary_error_test_inputs = binary_error_test_inputs_bff
