import matplotlib.pyplot as plt
import numpy as np

from aha import aha_segmental_values
from parameters.parameters import AHA_FEATURES, ANGULAR_COORDINATES, PLOT_COMPONENTS
from utils import plot_style


class BoundError(ValueError):
    """Related to plot boundaries"""


class BoundValueError(BoundError):
    """Related to out of range boundary values"""


class BoundNumberError(BoundError):
    """Related to incorrect number of boundary values"""


class AHAPlotBounds:
    """Class for drawing bounds of the plot"""

    def __init__(self, n_segments: int, ax: plt.Axes) -> None:
        self._n_segments = n_segments
        self.ax = ax

        self._bounds = AHA_FEATURES[self.n_segments]["bounds"]

        self.pu = plot_style.Alignment()

    @property
    def n_segments(self) -> str:
        return str(self._n_segments)

    @n_segments.setter
    def n_segments(self, n: int) -> None:
        if n not in (17, 18):
            raise aha_segmental_values.SegmentSizeError(
                f"Incorrect number of segmental values provided: {n=}. "
                "Provide either 17 or 18 elements."
            )

    def draw_aha_bounds(self) -> plt.Axes:
        self._draw_radial_bounds()
        self._draw_outer_bounds()
        self._draw_inner_bounds()
        return self.ax

    def _draw_radial_bounds(self) -> None:
        for radial_bound in self._bounds:
            self.ax.plot(
                ANGULAR_COORDINATES,
                np.repeat(float(radial_bound), ANGULAR_COORDINATES.shape),
                **PLOT_COMPONENTS["segment_border_style"],
            )

    def _draw_outer_bounds(self) -> None:
        """Draws the outer bounds of the plot

        Raises:
            BoundValueError: If the value of the boundary exceeds the range
        """
        bound_start = self._bounds[1]
        if (
            not PLOT_COMPONENTS["bound_range"]["inner"]
            <= bound_start
            <= PLOT_COMPONENTS["bound_range"]["outer"]
        ):
            raise BoundValueError(
                f"Inner starting point value must be between 0 and 1 (is {bound_start})"
            )
        bound_end = PLOT_COMPONENTS["bound_range"]["outer"]
        self._draw_bounds(bound_start, bound_end, 6)

    def _draw_inner_bounds(self) -> None:
        """Draws the inner bounds of the plot, depending on the number of segments

        Raises:
            BoundValueError: If the value of the boundary exceeds the range
        """
        bound_end = self._bounds[1]
        if (
            not PLOT_COMPONENTS["bound_range"]["inner"]
            <= bound_end
            <= PLOT_COMPONENTS["bound_range"]["outer"]
        ):
            raise BoundValueError(
                f"Inner starting point value must be between 0 and 1 (is {bound_end})"
            )
        if self.n_segments == "17":
            bound_start = self._bounds[0]
            if (
                not PLOT_COMPONENTS["bound_range"]["inner"]
                <= bound_start
                <= PLOT_COMPONENTS["bound_range"]["outer"]
            ):
                raise BoundValueError(
                    f"Inner starting point value must be between 0 and 1 (is {bound_start})"
                )
            self._draw_bounds(bound_start, bound_end, 4)
        else:
            self._draw_bounds(PLOT_COMPONENTS["bound_range"]["inner"], bound_end, 6)

    def _draw_bounds(self, inner: float, outer: float, n_borders: int) -> None:
        """Draws segment bounds in between levels.

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
        if not inner < outer:
            raise BoundValueError(f"Inner ({inner}) cannot be greater than outer ({outer})")
        if not n_borders in (4, 6):
            raise BoundNumberError(
                f"Only 4 or 6 borders between segments are allowed ({n_borders} provided)"
            )

        shift_function = self.pu.border_shift_functions[n_borders]

        for segment_border in range(n_borders):
            border_orientation = np.deg2rad(shift_function(segment_border))
            self.ax.plot(
                [border_orientation, border_orientation],
                [inner, outer],
                **PLOT_COMPONENTS["segment_border_style"],
            )
