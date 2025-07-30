"""Test HundermarkBinary model."""

import pytest

from auxi.mpp.slag.σ._hundermark_binary import HundermarkBinary
from auxi.mpp.slag.σ._hundermark_unary import HundermarkUnary

from ..test_parameters.binary_multi._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
    unary_vs_binary_test_inputs,
)


# tests that should pass
@pytest.mark.parametrize("temperature, composition", binary_testing_inputs)
def test_hundermark_binary(temperature: float, composition: dict[str, float]):
    """Test temperature and composition limits."""
    model = HundermarkBinary()
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition", binary_error_test_inputs)
def test_hundermark_binary_errors(temperature: float, composition: dict[str, float]):
    """Test if invalid inputs will fail."""
    model = HundermarkBinary()
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, composition", unary_vs_binary_test_inputs)
def test_ec_unary_vs_binary(temperature: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    unary_model = HundermarkUnary()
    binary_model = HundermarkBinary()

    compound = next(iter(composition.keys()))
    if compound != "SiO2":
        two_comps = {"SiO2": 0.0, f"{compound}": 1.0}
    else:
        two_comps = {"SiO2": 1.0, "Al2O3": 0.0}

    unary_result = unary_model.calculate(T=temperature, x=composition)
    binary_result = binary_model.calculate(T=temperature, x=two_comps)

    assert abs(binary_result - unary_result) <= 1e-9


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = HundermarkBinary()

    assert model.property == "Electrical Conductivity"
    assert model.symbol == "σ"
    assert model.display_symbol == "\\sigma"
    assert model.units == "\\siemens\\per\\meter"
    assert model.material == "Slag"
    assert model.references == ["hundermark2003-dissertation"]

    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = HundermarkBinary()
    result1 = model.calculate(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})
    result2 = model(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})

    assert abs(result1 - result2) < 1e-9
