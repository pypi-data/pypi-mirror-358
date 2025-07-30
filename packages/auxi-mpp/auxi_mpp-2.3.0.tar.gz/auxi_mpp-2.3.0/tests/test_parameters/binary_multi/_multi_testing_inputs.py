from .composition_parameters._binary_systems import composition_limits_binary
from .composition_parameters._multi_systems import (
    composition_limits_multi,
    composition_limits_multi_err,
)


# positive test temperature and composition tests
temperature_limits = [
    (1000, {"SiO2": 0.4, "Al2O3": 0.4, "CaO": 0.2}),
    (2500, {"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25}),
]

# compilation of multi tests
multi_testing_inputs = temperature_limits + composition_limits_multi

contain_sio2_err = [(1700, {"CaO": 0.2, "Al2O3": 0.2, "MgO": 0.2, "FeO": 0.2, "Fe2O3": 0.2})]
temperature_limits_err = [
    (2501, {"SiO2": 0.25, "CaO": 0.25, "MgO": 0.25, "FeO": 0.25}),
    (999, {"SiO2": 0.2, "CaO": 0.2, "MgO": 0.2, "FeO": 0.2, "Al2O3": 0.2}),
]
add_to_unity_err = [
    (1700, {"SiO2": 0.2, "Al2O3": 0.2, "CaO": 0.2, "MgO": 0.2, "FeO": 0.1}),
    (1700, {"SiO2": 0.2, "Al2O3": 0.2, "CaO": 0.2, "MgO": 0.2, "Fe2O3": 0.3}),
]
component_number_err = [(1700, {"SiO2": 0.6, "Al2O3": 0.4}), (1700, {"SiO2": 1.0})]
invalid_comp_err = [(1700, {"SiO2": 0.4, "Na2O": 0.4, "Al2O3": 0.2})]

# compilation of multi error tests
multi_error_test_inputs = (
    contain_sio2_err
    + temperature_limits_err
    + composition_limits_multi_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)

# test activity inputs
activity_tests: list[
    tuple[
        float,
        dict[str, float],
        dict[str, dict[str, float]],
    ]
] = [
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"Fe_liquid(liq)": {"Fe": 0.0}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"Fe_liquid(liq)": {"Fe": 0.5}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"Fe_liquid(liq)": {"Fe": 1.0}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"gas_ideal": {"O2": 0.0}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"gas_ideal": {"O2": 0.21}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"gas_ideal": {"O2": 1.0}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {}),
]


# activity error tests
activity_error_test_inputs = [
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"Fe_liquid(liq)": {"Fe": -0.01}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"Fe_liquid(liq)": {"Fe": 1.01}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"gas_ideal": {"O2": -0.01}}),
    (1700, {"SiO2": 0.25, "Fe2O3": 0.25, "CaO": 0.25, "FeO": 0.25}, {"gas_ideal": {"O2": 1.01}}),
    (1700, {"SiO2": 0.25, "Al2O3": 0.25, "CaO": 0.25, "MgO": 0.25}, {"Fe_liquid(liq)": {"Fe": 1.0}}),
]

# temperature limits for binary vs multi
temperature_limits_binary_vs_multi = [(1000, {"SiO2": 0.5, "Al2O3": 0.5}), (2500, {"SiO2": 0.5, "CaO": 0.5})]

# compare binary and multi model performance -- compilation of test parameters
binary_vs_multi_test_inputs = temperature_limits_binary_vs_multi + composition_limits_binary


# compare 3 vs 4 compounds provided with the same composition
multi3_vs_multi6_test_inputs = [
    (1000, {"SiO2": 0.4, "Al2O3": 0.4, "CaO": 0.2}),
    (2500, {"SiO2": 0.4, "CaO": 0.4, "Fe2O3": 0.2}),
    (1700, {"SiO2": 0.4, "Fe2O3": 0.4, "FeO": 0.2}),
    (1700, {"SiO2": 0.4, "FeO": 0.4, "MgO": 0.2}),
    (1700, {"SiO2": 0.4, "MgO": 0.4, "Al2O3": 0.2}),
]


pre_optimisation_params = [
    # pure substance conditions - unary and binaries
    # ternary systems
    {"AlO15": 0.2, "CaO": 0.2, "MgO": 0.0, "FeO": 0.0, "FeO15": 0.0},
    {"AlO15": 0.2, "CaO": 0.0, "MgO": 0.2, "FeO": 0.0, "FeO15": 0.0},
    # quaternary system
    {"AlO15": 0.2, "CaO": 0.2, "MgO": 0.2, "FeO": 0.0, "FeO15": 0.0},
    # 5-component system
    {"AlO15": 0.2, "CaO": 0.2, "MgO": 0.2, "FeO": 0.1, "FeO15": 0.0},
    # 6-component system
    {"AlO15": 0.2, "CaO": 0.2, "MgO": 0.2, "FeO": 0.1, "FeO15": 0.1},
]
