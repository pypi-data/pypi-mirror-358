"""Test ThibodeauBinary model."""

from collections.abc import Callable

import pytest

from auxi.mpp.slag.Vm._thibodeau_binary import ThibodeauBinary
from auxi.mpp.slag.Vm._thibodeau_unary import ThibodeauUnary

from ..test_parameters.binary_multi._binary_testing_inputs import unary_vs_binary_test_inputs
from ..test_parameters.binary_multi_bff_dependent._binary_testing_inputs import (
    binary_error_test_inputs,
    binary_testing_inputs,
)
from ..test_parameters.binary_multi_bff_dependent._dummy_bff import dummy_bff


# tests that should pass
@pytest.mark.parametrize("temperature, composition, bff", binary_testing_inputs)
def test_thibodeau_binary(
    temperature: float,
    composition: dict[str, float],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test temperature and composition limits."""
    model = ThibodeauBinary(bff=bff)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# tests that should fail
@pytest.mark.parametrize("temperature, composition, bff", binary_error_test_inputs)
def test_thibodeau_binary_errors(
    temperature: float,
    composition: dict[str, float],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test if invalid inputs will fail."""
    model = ThibodeauBinary(bff=bff)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# test against the unary model
@pytest.mark.parametrize("temperature, composition", unary_vs_binary_test_inputs)
def test_mv_unary_vs_binary(temperature: float, composition: dict[str, float]):
    """Test if unary and binary model agrees."""
    unary_model = ThibodeauUnary()
    binary_model = ThibodeauBinary(bff=dummy_bff)

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
    model = ThibodeauBinary(bff=dummy_bff)

    assert model.property == "Molar Volume"
    assert model.symbol == "Vm"
    assert model.display_symbol == "\\bar{V}"
    assert model.units == "\\cubic\\meter\\per\\mol"
    assert model.material == "Slag"
    assert model.references == ["thibodeau2016-part1", "thibodeau2016-part2"]

    assert model.bff == dummy_bff
    assert model.n_O["SiO2"] == 2
    assert model.cation["Al2O3"] == "Al"
    assert model.Q["CaO"][0]["a"] == 50.7
    assert model.Q["MgO"][4]["b"] == 0.7e-3
    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = ThibodeauBinary(bff=dummy_bff)
    result1 = model.calculate(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})
    result2 = model(T=1700, x={"SiO2": 0.5, "Al2O3": 0.5})

    assert abs(result1 - result2) < 1e-9
