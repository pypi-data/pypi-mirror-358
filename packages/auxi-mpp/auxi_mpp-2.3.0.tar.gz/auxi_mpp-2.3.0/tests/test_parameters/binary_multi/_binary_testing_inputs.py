from .composition_parameters._binary_systems import composition_limits_binary, composition_limits_binary_err


# positive test temperature and composition tests
temperature_limits = [(1000, {"SiO2": 0.5, "Al2O3": 0.5}), (2500, {"SiO2": 0.5, "Al2O3": 0.5})]

# compilation of binary tests
binary_testing_inputs = temperature_limits + composition_limits_binary

# error tests
contain_sio2_err = [
    (1700, {"CaO": 0.5, "Al2O3": 0.5}),
    (1700, {"MgO": 0.5, "CaO": 0.5}),
    (1700, {"Al2O3": 0.5, "MgO": 0.5}),
]
temperature_limits_err = [(2501, {"SiO2": 0.5, "Al2O3": 0.5}), (999, {"SiO2": 0.5, "CaO": 0.5})]
add_to_unity_err = [(1700, {"SiO2": 0.4, "CaO": 0.4}), (1700, {"SiO2": 0.6, "FeO": 0.6})]
component_number_err = [(1700, {"SiO2": 1.0}), (1700, {"SiO2": 0.4, "CaO": 0.4, "Al2O3": 0.2})]
invalid_comp_err = [(1700, {"SiO2": 0.5, "Na2O": 0.5})]

# compilation of binary error tests
binary_error_test_inputs = (
    contain_sio2_err
    + temperature_limits_err
    + composition_limits_binary_err
    + add_to_unity_err
    + component_number_err
    + invalid_comp_err
)

# compare unary and binary model performance
unary_vs_binary_test_inputs = [
    # temperature limits
    (1000, {"SiO2": 1.0}),
    (2500, {"SiO2": 1.0}),
    # pure substance conditions
    (1700, {"SiO2": 1.0}),
    (1700, {"Al2O3": 1.0}),
    (1700, {"CaO": 1.0}),
    (1700, {"FeO": 1.0}),
    (1700, {"Fe2O3": 1.0}),
    (1700, {"MgO": 1.0}),
]
