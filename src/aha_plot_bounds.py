import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray

import src.plot_style
import aha_segmental_values
from src.parameters import AHA_FEATURES, PLOT_COMPONENTS


class BoundError(ValueError):
    """Related to plot boundaries"""


class BoundValueError(BoundError):
    """Related to out of range boundary values"""


class BoundNumberError(BoundError):
    """Related to incorrect number of boundary values"""


class AHAPlotBounds:
    """Class for drawing bounds of the plot"""

    def __init__(self, segments: aha_segmental_values.AHASegmentalValues | list[float]) -> None:
        self.segments = segments
        self._theta: NDArray

        self.theta = np.linspace(0, 2 * np.pi, PLOT_COMPONENTS["resolution"][0])
        self._bounds = AHA_FEATURES[str(self.n_segments)]["bounds"]

        self.pu = src.plot_style.Alignment()

        _, self.ax = plt.subplots(
            figsize=(12, 8), nrows=1, ncols=1, subplot_kw={"projection": "polar"}
        )
        self.levels = None

    @property
    def segmental_values(self) -> list[float]:
        if isinstance(self.segments, list):
            return self.segments
        return list(self.segments.segmental_values())

    @property
    def n_segments(self) -> int:
        return len(self.segments)

    @property
    def theta(self) -> np.ndarray:
        return self._theta

    @theta.setter
    def theta(self, angles: np.ndarray):
        assert len(angles) == PLOT_COMPONENTS["resolution"][0], (
            f"Number of provided angle values {len(angles)} does not match the"
            f" desired resolution {self.ip.resolution[0]}"
        )
        self._theta = angles

    def draw_aha_bounds(self):
        self._draw_radial_bounds()
        self._draw_outer_bounds()
        self._draw_inner_bounds()

    def _draw_radial_bounds(self):
        for radial_bound in self._bounds:
            self.ax.plot(
                self.theta,
                np.repeat(float(radial_bound), self.theta.shape),
                **PLOT_COMPONENTS["segment_border_style"],
            )

    def _draw_outer_bounds(self):
        self._draw_bounds(self._bounds[1], 1, 6)

    def _draw_inner_bounds(self):
        if self.n_segments == 17:
            self._draw_bounds(self._bounds[0], self._bounds[1], 4)
        else:
            self._draw_bounds(0, self._bounds[1], 6)

    def _draw_bounds(self, inner: float, outer: float, n_borders: int):
        """Draws plot bounds in between levels.

        Args:
            inner:
                The level of the inner circle in the plot.
            outer:
                The level of the outer circle in the plot.
            n_borders:
                The number of borders to be drawn.

        Raises:
            BoundValueError: Thrown if the inner or outer levels are incorrect.
            BoundNumberError: Thrown if the wrong number of levels is provided.
        """
        if not 0 <= inner <= 1:
            raise BoundValueError(
                f"Inner starting point value must be between 0 and 1 (is {inner})"
            )
        if not 0 <= outer <= 1:
            raise BoundValueError(
                f"Outer starting point value must be between 0 and 1 (is {outer})"
            )
        if not inner < outer:
            raise BoundValueError(f"Inner ({inner}) cannot be greater than outer ({outer})")
        if not n_borders in (4, 6):
            raise BoundNumberError(
                f"Only 4 or 6 borders between segments are allowed ({n_borders} " f"provided)"
            )

        shift_function = self.pu.border_shift_functions[n_borders]

        for segment_border in range(n_borders):
            border_orientation = np.deg2rad(shift_function(segment_border))
            self.ax.plot(
                [border_orientation, border_orientation],
                [inner, outer],
                **PLOT_COMPONENTS["segment_border_style"],
            )
