"""Test HundermarkMulti model."""

import pytest

from auxi.mpp.slag.σ._hundermark_binary import HundermarkBinary
from auxi.mpp.slag.σ._hundermark_multi import HundermarkMulti

from ..test_parameters.binary_multi._multi_testing_inputs import (
    multi3_vs_multi6_test_inputs,
    multi_error_test_inputs,
    multi_testing_inputs,
)
from ..test_parameters.binary_multi.composition_parameters._binary_systems import composition_limits_binary


# tests that should pass
@pytest.mark.parametrize("temperature, composition", multi_testing_inputs)
def test_hundermark_multi(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = HundermarkMulti()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", multi_error_test_inputs)
def test_hundermark_multi_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = HundermarkMulti()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# test against the binary model
@pytest.mark.parametrize("temperature, composition", composition_limits_binary)
def test_ec_binary_vs_multi(temperature: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    binary_model = HundermarkBinary()
    multi_model = HundermarkMulti()

    six_comps = {"SiO2": 0.0, "Al2O3": 0.0, "CaO": 0.0, "FeO": 0.0, "Fe2O3": 0.0, "MgO": 0.0}
    for comp, value in composition.items():
        if comp in six_comps:
            six_comps[comp] = value

    binary_result = binary_model.calculate(T=temperature, x=composition)
    multi_result = multi_model.calculate(T=temperature, x=six_comps)

    assert abs(multi_result - binary_result) <= 1e-9


# test three and four component input for the same three component system
@pytest.mark.parametrize("temperature, composition", multi3_vs_multi6_test_inputs)
def test_ec_multi3_vs_multi6(temperature: float, composition: dict[str, float]):
    """Test if the multi model agrees when three and four components is specified."""
    multi3_model = HundermarkMulti()
    multi6_model = HundermarkMulti()

    six_comps = {"SiO2": 0.0, "Al2O3": 0.0, "CaO": 0.0, "FeO": 0.0, "Fe2O3": 0.0, "MgO": 0.0}
    for comp, value in composition.items():
        if comp in six_comps:
            six_comps[comp] = value

    multi3_result = multi3_model.calculate(T=temperature, x=composition)
    multi6_result = multi6_model.calculate(T=temperature, x=six_comps)

    assert abs(multi6_result - multi3_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = HundermarkMulti()

    assert model.property == "Electrical Conductivity"
    assert model.symbol == "σ"
    assert model.display_symbol == "\\sigma"
    assert model.units == "\\siemens\\per\\meter"
    assert model.material == "Slag"
    assert model.references == ["hundermark2003-dissertation"]

    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = HundermarkMulti()
    result1 = model.calculate(T=1700, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25})
    result2 = model(T=1700, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25})

    assert abs(result1 - result2) < 1e-9
