from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ...core.material_state import TpxState
from ..Vm import ThibodeauUnary
from ._model import Model


class ThibodeauDensityUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid oxide density model derived from Thibodeau's molar volume model.

    Returns:
       Density in [kg/m³].

    References:
        thibodeau2016-part1
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-part1"]

    molar_mass: dict[str, float] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = ThibodeauDensityUnary.data

        self.compound_scope: list[strCompoundFormula] = [c for c in list(data.keys())]
        self.molar_mass: dict[str, float] = {c: data[c]["molar mass"] for c in self.compound_scope}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate unary density.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":1.0}.
            a: Phase constituent activity dictionary. Not applicable to unary systems.

        Returns:
            Density in [kg/m³].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        # validate input
        state = TpxState(T=T, p=p, x=x)

        # ensure only one compound is given
        compound = list(state.x.keys())
        if len(compound) > 1:
            raise ValueError("Only one compound should be specified.")
        compound = compound[0]

        # validate input
        if compound not in self.compound_scope:
            raise ValueError(f"{compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        molar_volume_model = ThibodeauUnary()

        Vm = molar_volume_model.calculate(T=state.T, x=x)

        # get the molar mass of the specified compound
        molar_mass: float = self.molar_mass[compound]

        # scale to units of kg/m-3
        ρ = (molar_mass / Vm) * 1e-3

        return ρ


ThibodeauDensityUnary.load_data()
