from collections.abc import Callable
from math import factorial
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.stoichiometry import stoichiometry_coefficient as sc
from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateBinarySlagEquilibriumTpxState
from ._model import Model


class ThibodeauBinary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Binary liquid silicate slag molar volume model by Thibodeau.

    Args:
        bff : Bond fraction function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of bond fractions. Eg. def my_bff(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> dict[str, float]: ...

    Returns:
       Molar volume in [m³/mol].

    References:
        thibodeau2016-part1, thibodeau2016-part2
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-part1", "thibodeau2016-part2"]

    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]]
    n_O: dict[str, float] = Field(default_factory=dict)
    cation: dict[str, str] = Field(default_factory=dict)
    Q: dict[str, dict[int, dict[str, float]]] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        # add bff function validator

        data = ThibodeauBinary.data
        self.compound_scope = list(data.keys())

        self.n_O: dict[str, float] = {c: sc(c, "O") for c in self.compound_scope}
        self.cation: dict[str, str] = {c: data[c]["cation"] for c in self.compound_scope}
        self.Q: dict[str, dict[int, dict[str, float]]] = {c: data[c]["Q"] for c in self.compound_scope}  # type: ignore

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate binary system molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.5}.
            a: Phase constituent activity dictionary. Not applicable to binary systems.

        Returns:
            Molar volume in [m³/mol].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        # validate input
        state = SilicateBinarySlagEquilibriumTpxState(T=T, p=p, x=x)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # calcualte bond fractions
        x_b = self.bff(state.T, state.p, state.x, {})

        # equation 6 - total amount of oxygen atoms in the melt
        n_O_tot = sum([self.n_O[c] * state.x[c] for c in state.x.keys()])

        # equation 10 - amount M-O-M species in the melt
        n_MM = x_b[f"{self.cation[state.compound]}-{self.cation[state.compound]}"] * n_O_tot

        Q_c = self.Q[state.compound]
        V_m = 0.0

        # silica content is non-zero
        if abs(state.x["SiO2"]) > 1e-12:
            # equation 7 - amount of bridging oxygens (O^0) in the melt
            n_O0 = x_b["Si-Si"] * n_O_tot

            # equation 8 - probability Si-bonded oxygen being bridging oxygen
            P_O = n_O0 / (2 * state.x["SiO2"])

            # equation 9 - probability of Q^n species
            f = factorial
            W_n = [(f(4) / (f(4 - n) * f(n)) * P_O**n * (1 - P_O) ** (4 - n)) for n in range(5)]

            # equation 11 - amount of Q^n species in the melt
            n_Qn = [W_n[n] * state.x["SiO2"] for n in range(5)]

            # equation 12 - melt molar volume
            # term 1
            Q4_SiO2 = self.Q["SiO2"][4]
            V_m += n_Qn[4] * (Q4_SiO2["a"] + Q4_SiO2["b"] * state.T)

            # term 2
            V_m += sum([n_Qn[n] * (Q_c[n]["a"] + Q_c[n]["b"] * state.T) for n in range(4)])

        # term 3
        V_m += n_MM * (Q_c[4]["a"] + Q_c[4]["b"] * state.T)

        # scale Vm to return it in SI units
        V_m = V_m * 1e-6

        return V_m


ThibodeauBinary.load_data()
