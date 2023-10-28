from typing import Callable


class Alignment:
    """Class with functions used for aligning angles in the plot"""

    @staticmethod
    def _shift_by_60(x: int, correction: int = 0) -> int:
        return x * 60 + correction

    @staticmethod
    def _shift_by_90(x: int, correction: int = 90) -> int:
        return x * 90 + correction

    @property
    def shift_functions(self) -> dict[int, Callable]:
        return {4: self._shift_by_90, 6: self._shift_by_60}
