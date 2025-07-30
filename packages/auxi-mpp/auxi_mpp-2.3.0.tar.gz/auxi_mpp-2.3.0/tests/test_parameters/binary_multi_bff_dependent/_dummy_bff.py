def dummy_bff(T: float, p: float, x: dict[str, float], a: dict[str, dict[str, float]]) -> dict[str, float]:
    cations = {"SiO2": "Si", "Al2O3": "Al", "CaO": "Ca", "MgO": "Mg", "FeO": "Fe2+", "Fe2O3": "Fe3+"}

    test_bf: dict[str, float] = {
        f"{cations[k1]}-{cations[k2]}": v1 * v2 for k1, v1 in x.items() for k2, v2 in x.items()
    }

    return test_bf
