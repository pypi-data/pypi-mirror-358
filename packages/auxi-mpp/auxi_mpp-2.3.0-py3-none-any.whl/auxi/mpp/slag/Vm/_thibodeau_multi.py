import math
from collections.abc import Callable
from math import factorial
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.stoichiometry import stoichiometry_coefficient as sc
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateSlagEquilibriumTpxaState
from ._model import Model


class ThibodeauMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component silicate melt molar volume model by Thibodeau.

    Args:
        bff : Bond fraction function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of bond fractions. Eg. def my_bff(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> dict[str, float]: ...

    Returns:
       Molar volume in [m³/mol].

    References:
        thibodeau2016-part2, thibodeau2016-part3
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-part2", "thibodeau2016-part3"]

    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]]
    n_O: dict[str, float] = Field(default_factory=dict)
    cation: dict[str, str] = Field(default_factory=dict)
    Q: dict[str, dict[int, dict[str, float]]] = Field(default_factory=dict)
    cation_count: dict[str, int] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = ThibodeauMulti.data
        self.compound_scope = list(self.data.keys())

        self.n_O: dict[str, float] = {c: sc(c, "O") for c in self.compound_scope}
        self.cation: dict[str, str] = {c: data[c]["cation"] for c in self.compound_scope}
        self.Q: dict[str, dict[int, dict[str, float]]] = {c: data[c]["Q"] for c in self.compound_scope}  # type: ignore
        self.cation_count: dict[str, int] = {c: data[c]["cation-count"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.3, "FeO": 0.2}.
            a: Phase constituent activity dictionary. Eg. {"gas_ideal": {"O2": 0.21}}. Phase and constituent name depends on how the user set up the bond fraction function.

        Returns:
            Molar volume in [m³/mol].
        """
        # validate input
        state = SilicateSlagEquilibriumTpxaState(T=T, p=p, x=x, a=a)

        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # calcualte bond fractions
        x_b = self.bff(state.T, state.p, state.x, state.a)

        # part 1, equation 6 - total amount of oxygen atoms in the melt
        n_O_tot = sum([self.n_O[c] * state.x[c] for c in state.x.keys()])

        no_si_compounds = [c for c in state.compounds if c != "SiO2"]

        V_m: float = 0.0

        # part 2, equation 1 - melt molar volume
        # silica content is non-zero
        if abs(state.x["SiO2"]) > 1e-12:
            # part 1, equation 7 - amount of bridging oxygens (O^0) in the melt
            n_O0 = x_b["Si-Si"] * n_O_tot

            # part 1, equation 8 - probability Si-bonded oxygen being bridging oxygen
            P_O = n_O0 / (2 * state.x["SiO2"])

            # part 1, equation 9 - probability of Q^n species
            f = factorial
            W_n = [(f(4) / (f(4 - n) * f(n)) * P_O**n * (1 - P_O) ** (4 - n)) for n in range(5)]

            # part 1, equation 11 - amount of Q^n species in the melt
            n_Qn: list[float] = [W_n[n] * state.x["SiO2"] for n in range(5)]

            # part 2, equation 1 - melt molar volume
            # term 1
            Q4_SiO2 = self.Q["SiO2"][4]
            V_m += n_Qn[4] * (Q4_SiO2["a"] + Q4_SiO2["b"] * state.T)

            # term 2
            for n in range(4):
                si_m_interaction_list_numerator = [
                    x_b[f"Si-{self.cation[comp]}"] * (self.Q[comp][n]["a"] + self.Q[comp][n]["b"] * state.T)
                    for comp in no_si_compounds
                ]
                si_m_interaction_list_denominator = [float(x_b[f"Si-{self.cation[comp]}"]) for comp in no_si_compounds]

                denom = sum(si_m_interaction_list_denominator)
                if denom == 0 or math.isclose(denom, 0.0, abs_tol=1e-12):
                    continue
                V_m += n_Qn[n] * sum(si_m_interaction_list_numerator) / denom

        # term 3
        covered_by_ci: list[str] = []
        for ci in no_si_compounds:
            Q_ci = self.Q[ci]
            for cj in no_si_compounds:
                if cj in covered_by_ci:
                    continue
                Q_cj = self.Q[cj]
                x_ij = x_b[f"{self.cation[ci]}-{self.cation[cj]}"]
                a_ij = (Q_ci[4]["a"] + Q_cj[4]["a"]) / 2
                b_ij = (Q_ci[4]["b"] + Q_cj[4]["b"]) / 2

                V_m += n_O_tot * x_ij * (a_ij + b_ij * state.T)
            covered_by_ci.append(ci)

        # scale Vm to return it in SI units
        V_m = V_m * 1e-6

        return V_m


ThibodeauMulti.load_data()
