from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import F, R
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..D import ThibodeauIDMulti
from ..state import SilicateSlagEquilibriumTpxaState
from ..Vm import ThibodeauMulti
from ._model import Model


class ThibodeauECMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component silicate liquid oxide electrical conductivity model by Thibodeau.

    Args:
        bff : Bond fraction function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of bond fractions. Eg. def my_bff(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> dict[str, float]: ...

    Returns:
       Electrical conductivity in [S/m].

    References:
        thibodeau2016-ec
    """

    data: ClassVar[dict[str, dict[str, floatPositiveOrZero]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-ec", "thibodeau2016-dissertation"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]]

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

    def _get_Fe_fractions(self, x: dict[str, float]) -> tuple[float, float]:
        n_Fe2: float = x.get("FeO", 0.0)
        n_Fe3: float = x.get("Fe2O3", 0.0)

        n_Fe: float = n_Fe2 + n_Fe3

        if n_Fe == 0.0:
            return 0.0, 0.0
        else:
            return n_Fe2 / n_Fe, n_Fe3 / n_Fe

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system electrical conductivity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.3, "FeO": 0.2}.
            a: Phase constituent activity dictionary. Eg. {"gas_ideal": {"O2": 0.21}}. Phase and constituent name depends on how the user set up the bond fraction function.

        Returns:
            Electrical conductivity in [S/m].
        """
        # validate input
        state = SilicateSlagEquilibriumTpxaState(T=T, p=p, x=x, a=a)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        data = ThibodeauECMulti.data

        # ionic conduction contribution
        # calculate the molar volume
        melt_Vm_object = ThibodeauMulti(bff=self.bff)
        Vm = melt_Vm_object.calculate(T=state.T, p=state.p, x=state.x, a=state.a)

        # convert to m^3/mol to cm^3/mol
        Vm = Vm / 1e-6

        # eqn 7 - calculate diffusivity for each cation
        D_dict: dict[str, float] = ThibodeauIDMulti(bff=self.bff).calculate(T=state.T, p=state.p, x=state.x, a=state.a)

        # eqn 8 - sum of all cation contributions to electrical conductivity
        sigma_ionic: float = 0.0
        for comp in state.x:
            sigma_ionic += (
                100
                * ((data[comp]["z"] ** 2 * F**2) * (data[comp]["num_cats"] * state.x[comp]) * D_dict[comp])
                / ((R * state.T) * Vm)
            )

        # electronic conduction contribution
        sigma_electronic: float = 0.0

        if "FeO" in state.x.keys():
            # calculate the total Fe concentration
            total_n_Fe2_Fe3: float = 0.0
            if "FeO" in state.x:
                total_n_Fe2_Fe3 += data["FeO"]["num_cats"] * state.x["FeO"]

            if "Fe2O3" in state.x:
                total_n_Fe2_Fe3 += data["Fe2O3"]["num_cats"] * state.x["Fe2O3"]

            total_Fe_concentration: float = total_n_Fe2_Fe3 / Vm
            # calculate Fe2+ and Fe3+ fractions
            FeII, FeIII = self._get_Fe_fractions(x)
            # eqn 29 dissertation - calculate electronic contribution
            sigma_electronic += 100 * (
                (float(data["FeO"]["A"]) / state.T) * D_dict["FeO"] * total_Fe_concentration**2 * FeII * FeIII
            )

        sigma: float = sigma_ionic + sigma_electronic

        return sigma


ThibodeauECMulti.load_data()
