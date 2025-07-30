# binary systems -- positive tests
sio2_al2o3 = [
    (1700, {"SiO2": 1.0, "Al2O3": 0.0}),
    (1700, {"SiO2": 0.0, "Al2O3": 1.0}),
    (1700, {"SiO2": 0.5, "Al2O3": 0.5}),
]
sio2_cao = [
    (1700, {"SiO2": 1.0, "CaO": 0.0}),
    (1700, {"SiO2": 0.0, "CaO": 1.0}),
    (1700, {"SiO2": 0.5, "CaO": 0.5}),
]
sio2_fe2o3 = [
    (1700, {"SiO2": 1.0, "Fe2O3": 0.0}),
    (1700, {"SiO2": 0.0, "Fe2O3": 1.0}),
    (1700, {"SiO2": 0.5, "Fe2O3": 0.5}),  # 8
]
sio2_feo = [
    (1700, {"SiO2": 1.0, "FeO": 0.0}),
    (1700, {"SiO2": 0.0, "FeO": 1.0}),
    (1700, {"SiO2": 0.5, "FeO": 0.5}),
]
sio2_mgo = [
    (1700, {"SiO2": 1.0, "MgO": 0.0}),
    (1700, {"SiO2": 0.0, "MgO": 1.0}),
    (1700, {"SiO2": 0.5, "MgO": 0.5}),
]

# compilation of binary positive test parameters
composition_limits_binary = sio2_al2o3 + sio2_cao + sio2_fe2o3 + sio2_feo + sio2_mgo

# binary systems -- error tests
sio2_al2o3_err = [(1700, {"SiO2": 1.01, "Al2O3": -0.01}), (1700, {"SiO2": -0.01, "Al2O3": 1.01})]
sio2_cao_err = [(1700, {"SiO2": 1.01, "CaO": -0.01}), (1700, {"SiO2": -0.01, "CaO": 1.01})]
sio2_fe2o3_err = [(1700, {"SiO2": 1.01, "Fe2O3": -0.01}), (1700, {"SiO2": -0.01, "Fe2O3": 1.01})]
sio2_feo_err = [(1700, {"SiO2": 1.01, "FeO": -0.01}), (1700, {"SiO2": -0.01, "FeO": 1.01})]
sio2_mgo_err = [(1700, {"SiO2": 1.01, "MgO": -0.01}), (1700, {"SiO2": -0.01, "MgO": 1.01})]

# compilation of binary error test parameters
composition_limits_binary_err = sio2_al2o3_err + sio2_cao_err + sio2_fe2o3_err + sio2_feo_err + sio2_mgo_err
