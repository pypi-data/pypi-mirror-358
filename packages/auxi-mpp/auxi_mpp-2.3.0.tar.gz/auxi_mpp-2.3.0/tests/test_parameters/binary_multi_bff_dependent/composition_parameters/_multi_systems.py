from collections.abc import Callable

from ...binary_multi.composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)
from .._dummy_bff import dummy_bff


# normal tests
composition_limits_multi_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in composition_limits_multi:
    tup_bff = (*tup, dummy_bff)
    composition_limits_multi_bff.append(tup_bff)

# reuse original name
composition_limits_multi = composition_limits_multi_bff


# tests that should fail
composition_limits_multi_err_bff: list[
    tuple[
        float,
        dict[str, float],
        Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
    ]
] = []

for tup in composition_limits_multi_err:
    tup_bff = (*tup, dummy_bff)
    composition_limits_multi_err_bff.append(tup_bff)

# reuse original name
composition_limits_multi_err = composition_limits_multi_err_bff
