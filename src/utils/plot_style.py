from typing import Callable


class Alignment:
    """Class with functions used for aligning angles in the plot"""

    @staticmethod
    def _shift_by_60(x: int) -> int:
        return x * 60

    @staticmethod
    def _shift_by_60_with_correction(x: int) -> int:
        return x * 60 + 90

    @staticmethod
    def _shift_by_90(x: int) -> int:
        return x * 90

    @staticmethod
    def _shift_by_90_with_correction(x: int) -> int:
        return x * 90 - 45

    @property
    def border_shift_functions(self) -> dict[int, Callable]:
        return {4: self._shift_by_90_with_correction, 6: self._shift_by_60}

    @property
    def annotation_shift_functions(self) -> dict[int, Callable]:
        return {4: self._shift_by_90, 6: self._shift_by_60_with_correction}
