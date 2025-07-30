from typing import Any, ClassVar

from pydantic import Field

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ...core.material_state import TpxState
from ._model import Model


class ThibodeauUnary(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Unary liquid oxide molar volume model by Thibodeau.

    Returns:
       Molar volume in [m³/mol].

    References:
        thibodeau2016-part1
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["thibodeau2016-part1"]

    a: floatPositiveOrZero = 0.0
    b: floatPositiveOrZero = 0.0
    oxygen_number: int = 0
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        self.compound_scope = list(self.data.keys())

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, floatFraction]] = {},
    ) -> float:
        """
        Calculate unary molar volume.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":1.0}.
            a: Phase constituent activity dictionary. Not applicable to unary systems.

        Returns:
            Molar volume in [m³/mol].
        """
        if a != {}:
            raise ValueError("Specifying activities is only applicable to multi-component models.")

        data = ThibodeauUnary.data

        # validate T input
        state = TpxState(T=T, p=p, x=x)
        # ensure only one compound is given
        compound = list(state.x.keys())
        if len(compound) > 1:
            raise ValueError("Only one compound should be specified.")
        compound = compound[0]

        # validate input
        if compound not in self.compound_scope:
            raise ValueError(f"{compound} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        self.a = data[compound]["a"]
        self.b = data[compound]["b"]
        self.oxygen_number = data[compound]["oxygen-number"]

        # SiO2 parameters are Si oriented, whereas MO's are O oriented

        if compound != "SiO2":
            # amount of M-O-M units determined by oxygen count (multiplication by oxygen count)
            V_m = self.oxygen_number * (self.a + self.b * state.T)
        else:
            # fraction of Q_4 species is unity for pure SiO2 (multiplication by 1)
            V_m = self.a + self.b * state.T

        # scale Vm to return it in SI units
        V_m = V_m * 1e-6
        return V_m


ThibodeauUnary.load_data()
