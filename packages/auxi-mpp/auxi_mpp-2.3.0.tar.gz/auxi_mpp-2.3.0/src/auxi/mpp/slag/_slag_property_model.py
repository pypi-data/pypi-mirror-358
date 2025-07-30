import inspect
from pathlib import Path
from typing import Any

from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..core import MaterialPropertyModel
from ..core._material_type import MaterialType


class SlagPropertyModel[
    T: floatPositiveOrZero,
    p: floatPositiveOrZero,
    x: dict[str, floatFraction],
    a: dict[str, dict[str, floatFraction]],
](MaterialPropertyModel[T, p, x, a]):
    material_type: MaterialType = MaterialType.SLAG_LIQUID
    material: strNotEmpty = "Slag"

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        if len(SlagPropertyModel.data) == 0:
            SlagPropertyModel.load_data(path=Path(inspect.getfile(type(self))))
