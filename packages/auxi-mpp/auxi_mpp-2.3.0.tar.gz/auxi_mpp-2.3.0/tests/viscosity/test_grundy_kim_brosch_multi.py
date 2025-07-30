"""Test GrundyKimBroschMulti model."""

from collections.abc import Callable
from typing import Any

import pytest

from auxi.mpp.slag.state import SilicateSlagEquilibriumTpxaState
from auxi.mpp.slag.μ._grundy_kim_brosch_binary import GrundyKimBroschBinary
from auxi.mpp.slag.μ._grundy_kim_brosch_multi import GrundyKimBroschMulti

from ..test_parameters.binary_multi._multi_testing_inputs import multi3_vs_multi6_test_inputs, pre_optimisation_params
from ..test_parameters.binary_multi.composition_parameters._binary_systems import composition_limits_binary
from ..test_parameters.binary_multi_bff_dependent._dummy_bff import dummy_bff
from ..test_parameters.binary_multi_bff_dependent._multi_testing_inputs import (
    activity_error_test_inputs,
    activity_tests,
    multi_error_test_inputs,
    multi_testing_inputs,
)


# tests that should pass
# general
@pytest.mark.parametrize("temperature, composition, bff", multi_testing_inputs)
def test_grundy_kim_brosch_multi(
    temperature: float,
    composition: dict[str, float],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test temperature and composition limits."""
    model = GrundyKimBroschMulti(bff=bff)
    result = model.calculate(T=temperature, x=composition)

    assert result > 0


# activity tests
@pytest.mark.parametrize("temperature, composition, activities, bff", activity_tests)
def test_grundy_kim_brosch_multi_activity(
    temperature: float,
    composition: dict[str, float],
    activities: dict[str, dict[str, float]],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test activity limits."""
    model = GrundyKimBroschMulti(bff=bff)
    result = model.calculate(T=temperature, x=composition, a=activities)

    assert result > 0


# tests that should fail
# general
@pytest.mark.parametrize("temperature, composition, bff", multi_error_test_inputs)
def test_grundy_kim_brosch_multi_errors(
    temperature: float,
    composition: dict[str, float],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test if invalid inputs will fail."""
    model = GrundyKimBroschMulti(bff=bff)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition)


# activity tests
@pytest.mark.parametrize("temperature, composition, activities, bff", activity_error_test_inputs)
def test_grundy_kim_brosch_activity_errors(
    temperature: float,
    composition: dict[str, float],
    activities: dict[str, dict[str, float]],
    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]],
):
    """Test if invalid inputs will fail."""
    model = GrundyKimBroschMulti(bff=bff)
    with pytest.raises(ValueError):
        model.calculate(T=temperature, x=composition, a=activities)


# test against the binary model
@pytest.mark.parametrize("temperature, composition", composition_limits_binary)
def test_viscosity_binary_vs_multi(temperature: float, composition: dict[str, float]):
    """Test if the binary and multi model agrees."""
    binary_model = GrundyKimBroschBinary(bff=dummy_bff)
    multi_model = GrundyKimBroschMulti(bff=dummy_bff)

    six_comps = {"SiO2": 0.0, "Al2O3": 0.0, "CaO": 0.0, "MgO": 0.0, "FeO": 0.0, "Fe2O3": 0.0}
    for comp, value in composition.items():
        if comp in six_comps:
            six_comps[comp] = value

    binary_result = binary_model.calculate(T=temperature, x=composition)
    multi_result = multi_model.calculate(T=temperature, x=six_comps)

    assert abs(multi_result - binary_result) <= 1e-9


# test three and four component input for the same three component system
@pytest.mark.parametrize("temperature, composition", multi3_vs_multi6_test_inputs)
def test_viscosity_multi3_vs_multi6(temperature: float, composition: dict[str, float]):
    """Test if the multi model agrees when three and four components is specified."""
    multi3_model = GrundyKimBroschMulti(bff=dummy_bff)
    multi6_model = GrundyKimBroschMulti(bff=dummy_bff)

    six_comps = {"SiO2": 0.0, "Al2O3": 0.0, "CaO": 0.0, "MgO": 0.0, "FeO": 0.0, "Fe2O3": 0.0}
    for comp, value in composition.items():
        if comp in six_comps:
            six_comps[comp] = value

    multi3_result = multi3_model.calculate(T=temperature, x=composition)
    multi6_result = multi6_model.calculate(T=temperature, x=six_comps)

    assert abs(multi6_result - multi3_result) <= 1e-8


def test_loaded_parameters():
    """Test if parameters loads normally."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    assert model.property == "Dynamic Viscosity"
    assert model.symbol == "μ"
    assert model.display_symbol == "\\mu"
    assert model.units == "\\pascal\\second"
    assert model.material == "Slag"
    assert model.references == ["grundy2008-part1", "grundy2008-part2"]

    assert model.bff == dummy_bff
    assert model.names["AlO15"] == "Al2O3"
    assert model.cation["SiO2"] == "Si"
    assert model.struc_unit["Al2O3"] == "AlO15"
    assert model.struc_ox_count["CaO"] == 1
    assert model.parameters["MgO"]["A"] == -10.58
    assert model.cation_count["Al2O3"] == 2
    assert model.equilibrium_stoic["CaO"] == 1
    assert model.molar_mass["MgO"] == 40.30
    assert sorted(model.compound_scope) == ["Al2O3", "CaO", "Fe2O3", "FeO", "MgO", "SiO2"]

    model.calculate(T=1700, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25})

    assert sorted(list(model.structural_x.keys())) == ["AlO15", "CaO", "MgO", "SiO2"]


def test_abstract_calc():
    """Test if calling the calculate() method implicitly works correctly."""
    model = GrundyKimBroschMulti(bff=dummy_bff)
    result1 = model.calculate(T=1700, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25})
    result2 = model(T=1700, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25})

    assert abs(result1 - result2) < 1e-9


# model specific functions
def test_structural_and_full_fractions():
    """Test the conversion to structural and to full fractions."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    state = SilicateSlagEquilibriumTpxaState(
        T=1500, p=101325, x={"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25}, a={}
    )

    x_struc_unit = model._structural_fractions(state)  # type: ignore

    assert x_struc_unit["AlO15"] == 0.4

    full_fracs = model._full_fractions(x_struc_unit)  # type: ignore

    assert full_fracs["Al2O3"] == 0.25


def test_normalise_fractions():
    """Test if the function normalises."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    composition = {"SiO2": 2, "Al2O3": 1, "CaO": 1}
    normalised_comp = model._normalise_fractions(composition)  # type: ignore
    assert abs(normalised_comp["SiO2"] - 0.5) < 1e-9

    composition = {"SiO2": 0.1, "MgO": 0.6, "Al2O3": 0.05, "CaO": 0.05}
    normalised_comp = model._normalise_fractions(composition)  # type: ignore
    assert abs(normalised_comp["MgO"] - 0.75) < 1e-9


def test_count_oxygens():
    """Test if the oxygens per mole is counted correctly."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    n_oxygens = model._count_oxygens({"SiO2": 0.5, "AlO15": 0.5, "MgO": 0.0})  # type: ignore

    assert n_oxygens == 1.75


def test_prepare_params_for_optimisation():
    """Test is pre-optimization parameters loads correctly."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    composition = {"SiO2": 0.25, "CaO": 0.2, "AlO15": 0.2, "FeO": 0.2, "FeO15": 0.15}

    params, lists = model._prepare_params_for_optimisation(composition)  # type: ignore

    c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5 = params
    _, missing_comps, _ = lists

    assert c1 == 2
    assert c2 == 1
    assert c3 == 1
    assert c4 == 1
    assert c5 == 2
    assert a1 == 1
    assert a2 == 1
    assert a3 == 1
    assert a4 == 1
    assert C1 == 0.2
    assert C2 == 0.2
    assert C3 == 0.0
    assert C4 == 0.2
    assert C5 == 0.15

    assert missing_comps == ["MgO"]


@pytest.mark.parametrize(
    "struc_composition",
    pre_optimisation_params,
)
def test_find_solutions(struc_composition: dict[str, float]):
    """Test if the shgo optimiser will find solutions at the full composition range."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    c1: float = 2.0
    c2: float = 1.0
    c3: float = 1.0
    c4: float = 1.0
    c5: float = 2.0
    a1: float = 1.0
    a2: float = 1.0
    a3: float = 1.0
    a4: float = 1.0
    C1: float = struc_composition["AlO15"]
    C2: float = struc_composition["CaO"]
    C3: float = struc_composition["MgO"]
    C4: float = struc_composition["FeO"]
    C5: float = struc_composition["FeO15"]
    params: tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float] = (
        c1,
        c2,
        c3,
        c4,
        c5,
        a1,
        a2,
        a3,
        a4,
        C1,
        C2,
        C3,
        C4,
        C5,
    )

    dummy_list = []

    associates = ["CaAl2O4", "MgAl2O4", "FeAl2O4", "CaFe2O4"]
    lists: tuple[list[Any], list[Any], list[Any]] = dummy_list, dummy_list, associates

    # assume K values of 10
    const_K: dict[str, float] = {associates[0]: 10, associates[1]: 10, associates[2]: 10, associates[3]: 10}

    sio2_fraction = 1.0 - sum(struc_composition.values())
    struc_composition["SiO2"] = sio2_fraction

    (
        solution_x1,
        solution_x2,
        solution_x3,
        solution_x4,
    ) = model._find_solutions(params, lists, const_K, struc_composition)  # type: ignore

    assert solution_x1 >= 0
    assert solution_x2 >= 0
    assert solution_x3 >= 0
    assert solution_x4 >= 0

    assert solution_x1 < 1
    assert solution_x2 < 1
    assert solution_x3 < 1
    assert solution_x4 < 1


def test_calc_x_star():
    """Test if SiO2 amount increases and AlO15 decreases when counting the associates with SiO2."""
    model = GrundyKimBroschMulti(bff=dummy_bff)

    composition = {"SiO2": 0.5, "CaO": 0.2, "AlO15": 0.15, "MgO": 0.05, "FeO": 0.05, "FeO15": 0.05}

    c1: float = 2.0
    c2: float = 1.0
    c3: float = 1.0
    c4: float = 1.0
    c5: float = 2.0
    a1: float = 1.0
    a2: float = 1.0
    a3: float = 1.0
    a4: float = 1.0
    C1: float = composition["AlO15"]
    C2: float = composition["CaO"]
    C3: float = composition["MgO"]
    C4: float = composition["FeO"]
    C5: float = composition["FeO15"]
    params: tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float] = (
        c1,
        c2,
        c3,
        c4,
        c5,
        a1,
        a2,
        a3,
        a4,
        C1,
        C2,
        C3,
        C4,
        C5,
    )

    non_sio2 = ["AlO15", "CaO", "MgO", "FeO", "FeO15"]
    missing_comps = []
    associates = ["CaAl2O4", "MgAl2O4", "FeAl2O4", "CaFe2O4"]
    lists: tuple[list[Any], list[Any], list[Any]] = non_sio2, missing_comps, associates

    solutions = 0.01, 0.02, 0.03, 0.04

    X_star = model._calc_x_star(params, lists, solutions, composition)  # type: ignore

    assert X_star["SiO2"] > composition["SiO2"]
    assert X_star["AlO15"] < composition["AlO15"]
    assert X_star["CaO"] < composition["CaO"]
    assert X_star["MgO"] < composition["MgO"]
    assert X_star["FeO"] < composition["FeO"]
    assert X_star["FeO15"] < composition["FeO15"]


def test_remove_SiO2():
    """Test is SiO2 is removed."""
    model = GrundyKimBroschMulti(bff=dummy_bff)
    non_sio2_list = model._remove_SiO2(["SiO2", "MgO", "CaO"])  # type: ignore

    assert "SiO2" not in non_sio2_list
    assert non_sio2_list == ["MgO", "CaO"]


def test_gcd_a_b_c():
    """Test is the greated common divisor is found."""
    model = GrundyKimBroschMulti(bff=dummy_bff)
    list_coeffs = [10, 4, 6, 2, 8, 10, 4, 6, 2]

    result = model._gcd_a_b_c(list_coeffs)  # type: ignore
    c1, c2, c3, c4, c5, a1, a2, a3, a4 = result

    assert c1 == 5
    assert c2 == 2
    assert c3 == 3
    assert c4 == 1
    assert c5 == 4
    assert a1 == 5
    assert a2 == 2
    assert a3 == 3
    assert a4 == 1
