from typing import Any, Self

from pydantic import Field, model_validator

from auxi.chemistry.validation import listCompoundFormulas
from auxi.core.validation import floatFraction, floatPositiveOrZero

from ...core.material_state import MaterialState


class SilicateSlagEquilibriumTpxaState(MaterialState):
    """
    Generate a temperature and composition state for a multi-component silicate slag.

    Args:
    ----
        T : [K] Temperature.
        p : [Pa] Pressure.
        x : Mole fraction of slag components.
        a : Phase constituent activities.

    Raises:
    ------
        ValueError: If SiO2 is not one of the compounds.
        ValueError: If less than 2 components is specified.
    """

    T: floatPositiveOrZero
    p: floatPositiveOrZero
    x: dict[str, floatFraction]
    a: dict[str, dict[str, float]]
    compounds: listCompoundFormulas = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    @model_validator(mode="after")
    def check_model(self) -> Self:
        compounds: set[str] = set(self.x.keys())
        self.compounds = list(compounds)

        if "SiO2" not in compounds:
            raise ValueError("SiO2 must be one of the compounds.")

        if len(compounds) <= 2:
            raise ValueError("Three or more compounds must be specified.")

        if self.T < 1000 or self.T > 2500:
            raise ValueError("Temperature should be above 1000 K and below 2500 K.")

        total_mole_frac = 0
        for comp in self.x:
            total_mole_frac += self.x[comp]

        if abs(total_mole_frac - 1.00) > 1e-9:
            raise ValueError("Mole fractions should add up to 1.00.")

        # ensure iron oxide is present when Fe liquid activity is specified
        if self.x.get("FeO", 0.0) + self.x.get("Fe2O3", 0.0) == 0.0:
            if "Fe_liquid(liq)" in self.a:
                raise ValueError("Fe_liquid(liq) activity should not be specified if no iron oxide is present.")

        # test for valid activity values
        if self.a != {}:
            phases = list(self.a.keys())
            for ph in phases:
                constituents = list(self.a[ph].keys())
                for pc in constituents:
                    if self.a[ph][pc] > 1.0 or self.a[ph][pc] < 0.0:
                        raise ValueError(
                            "Invalid activity provided. Activities must be a value from zero to unity, inclusive."
                        )

        return self

    def _init(self):
        return
