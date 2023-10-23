from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from src.parameters.parameters import (
    ANGULAR_COORDINATES,
    BIOMARKER_FEATURES,
    PLOT_COMPONENTS,
    RADIAL_COORDINATES,
)


class Biomarker:
    """Base class for biomarker coloring handling"""

    def __init__(self) -> None:
        self._extended_radial_coordinates = np.repeat(
            RADIAL_COORDINATES[:, np.newaxis], PLOT_COMPONENTS["resolution"][0], axis=1
        ).T

        self._extended_angular_coordinates = np.repeat(
            ANGULAR_COORDINATES[:, np.newaxis], self.extended_radial_coordinates.shape[1], axis=1
        )

    @property
    def biomarker_name(self) -> str:
        return ""

    @property
    def norm(self) -> tuple[int, int]:
        return (0, 0)

    @property
    def cmap(self) -> plt.Colormap:
        return plt.get_cmap(BIOMARKER_FEATURES[self.biomarker_name]["cmap"])

    @property
    def units(self) -> str:
        return BIOMARKER_FEATURES[self.biomarker_name]["units"]

    @property
    def title(self) -> str:
        return BIOMARKER_FEATURES[self.biomarker_name]["title"]

    @property
    def extended_radial_coordinates(self) -> NDArray:
        return self._extended_radial_coordinates

    @property
    def extended_angular_coordinates(self) -> NDArray:
        return self._extended_angular_coordinates

    def color_plot(self, ax: plt.Axes, interpolated_segment_values: NDArray) -> plt.Axes:
        """Virtual function with unused arguments."""
        _ = (
            ax,
            interpolated_segment_values,
        )
        return ax


def validate_resolution(func: Callable) -> Callable:
    """Validates the resultion of the provided interpolation values used for coloring.

    Args:
        func: Coloring function
    """

    def wrapper(self: Biomarker, ax: plt.Axes, interpolated_segment_values: NDArray) -> plt.Axes:
        assert interpolated_segment_values.shape[0] == self.extended_angular_coordinates.shape[0], (
            "Incorrect resolution of interpolation in angular axis "
            f"({interpolated_segment_values.shape[0]}) "
            f"compared to coloring resolution ({self.extended_angular_coordinates.shape[0]})"
        )

        assert interpolated_segment_values.shape[1] == self.extended_radial_coordinates.shape[0], (
            f"Incorrect resolution of interpolation in radial axis "
            f"({interpolated_segment_values.shape[0]}) "
            f"compared to coloring resolution ({self.extended_radial_coordinates.shape[0]})"
        )
        return func(self, ax, interpolated_segment_values)

    return wrapper
