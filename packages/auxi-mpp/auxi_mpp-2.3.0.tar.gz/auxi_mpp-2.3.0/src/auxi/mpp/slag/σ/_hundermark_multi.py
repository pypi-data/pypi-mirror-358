import math
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateSlagEquilibriumTpxaState
from ._model import Model


class HundermarkMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component silicate liquid oxide electrical conductivity model by Hundermark.

    Returns:
       Electrical conductivity in [S/m].

    References:
        hundermark2003-dissertation
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["hundermark2003-dissertation"]
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

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
            a: Phase constituent activity dictionary. Not applicable to Hundermark's model.

        Returns:
            Electrical conductivity in [S/m].
        """
        if a != {}:
            raise ValueError(
                "Specifying activities is not applicable to Hundermark's model as it is not a structure based model."
            )

        # validate input
        state = SilicateSlagEquilibriumTpxaState(T=T, p=p, x=x, a=a)

        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        data = HundermarkMulti.data

        # sum of all oxide contributions to electrical conductivity
        ln_sigma: float = 0.0
        if ("FeO" in x and x["FeO"] > 0.0) or ("Fe2O3" in x and x["Fe2O3"] > 0.0):
            # eqn 34
            for comp in state.x:
                ln_sigma += (data[comp]["param"]["A2"] + (data[comp]["param"]["B2"] / state.T)) * x[comp]

            ln_sigma += (data["FeO"]["param"]["A_eq"] - (data["FeO"]["param"]["B_eq"] / state.T)) * (
                x.get("Fe2O3", 0) * x.get("FeO", 0)
            )
        else:
            # eqn 32
            for comp in state.x:
                if comp in {"FeO", "Fe2O3"}:
                    continue
                else:
                    ln_sigma += (data[comp]["param"]["A1"] + (data[comp]["param"]["B1"] / state.T)) * x[comp]

        sigma: float = 100 * math.exp(ln_sigma)  # S/m

        return sigma


HundermarkMulti.load_data()
