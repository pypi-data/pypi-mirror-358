import math
from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ...core.material_state import TpxState
from ._model import Model


class HundermarkUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid oxide electrical conductivity model by Hundermark.

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
        Unary electrical conductivity model.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":1.0}.
            a: Phase constituent activity dictionary. Not applicable to unary systems.

        Returns:
            Electrical conductivity in [S/m]].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        data = HundermarkUnary.data

        # validate T input
        state = TpxState(T=T, p=p, x=x)

        # ensure only one compound is given
        compound = list(x.keys())
        if len(compound) > 1:
            raise ValueError("Only one compound should be specified.")
        compound = compound[0]

        if compound not in self.compound_scope:
            raise ValueError(f"{compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # eqn 34 - sum of all oxide contributions to electrical conductivity
        ln_sigma: float = 0.0
        for comp in state.x:
            ln_sigma += (data[comp]["param"]["A"] + (data[comp]["param"]["B"] / state.T)) * x[comp]

        sigma: float = 100 * math.exp(ln_sigma)  # S/m

        return sigma


HundermarkUnary.load_data()
