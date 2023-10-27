from __future__ import annotations

from typing import Callable

import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt
from matplotlib import ticker
from numpy.typing import NDArray

from parameters.parameters import (
    ANGULAR_COORDINATES,
    BIOMARKER_FEATURES,
    PLOT_COMPONENTS,
    RADIAL_COORDINATES,
)


def validate_resolution(func: Callable) -> Callable:
    """Validates the resultion of the provided interpolation values used for coloring.

    Args:
        func: Coloring function
    """

    def wrapper(self: Biomarker, ax: plt.Axes, interpolated_segment_values: NDArray) -> plt.Axes:
        assert interpolated_segment_values.shape[0] == self.extended_angular_coordinates.shape[1], (
            "Incorrect resolution of interpolation in angular axis "
            f"({interpolated_segment_values.shape[0]}) "
            f"compared to coloring resolution ({self.extended_angular_coordinates.shape[1]})"
        )

        assert interpolated_segment_values.shape[1] == self.extended_radial_coordinates.shape[0], (
            f"Incorrect resolution of interpolation in radial axis "
            f"({interpolated_segment_values.shape[1]}) "
            f"compared to coloring resolution ({self.extended_radial_coordinates.shape[0]})"
        )
        return func(self, ax, interpolated_segment_values)

    return wrapper


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
    def norm(self) -> tuple[int, int]:
        return (0, 0)

    @property
    def cmap(self) -> plt.colormaps:
        return plt.get_cmap(BIOMARKER_FEATURES[self.__class__.__name__]["cmap"])

    @property
    def units(self) -> str:
        return BIOMARKER_FEATURES[self.__class__.__name__]["units"]

    @property
    def title(self) -> str:
        return BIOMARKER_FEATURES[self.__class__.__name__]["title"]

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


class Strain(Biomarker):
    """Class for coloring the AHA plot with strain values"""

    @property
    def norm(self) -> colors.BoundaryNorm:
        norm = colors.BoundaryNorm(self.levels, ncolors=self.cmap.N, clip=True)
        return norm

    @property
    def levels(self) -> ticker.MaxNLocator:
        nbins = BIOMARKER_FEATURES[self.__class__.__name__]["n_bins"]
        tick_values = BIOMARKER_FEATURES[self.__class__.__name__]["tick_values"]
        return ticker.MaxNLocator(nbins=nbins).tick_values(*tick_values)

    @validate_resolution
    def color_plot(self, ax: plt.Axes, interpolated_segment_values: NDArray) -> plt.Axes:
        """Color plot according to the strain visualisation guidelines.

        Args:
            ax: Plot object.
            interpolated_segment_values: Values used for coloring the plot.

        Returns:
            pyplot.Axes: Colored plot object.
        """
        ax.contourf(
            self.extended_angular_coordinates,
            self.extended_radial_coordinates,
            interpolated_segment_values.T,
            cmap=self.cmap,
            levels=self.levels,
        )

        return ax


class MyocardialWork(Biomarker):
    """Class for coloring the AHA plot with myocardial work values"""

    @property
    def norm(self) -> tuple[int, int]:
        norm = tuple(BIOMARKER_FEATURES[self.__class__.__name__]["norm_values"])
        normalized_norm = colors.Normalize(vmin=norm[0], vmax=norm[1])
        return normalized_norm

    @validate_resolution
    def color_plot(self, ax: plt.Axes, interpolated_segment_values: NDArray) -> plt.Axes:
        """Color plot according to the myocardial work visualisation guidelines.

        Args:
            ax: Plot object.
            interpolated_segment_values: Values used for coloring the plot.

        Returns:
            pyplot.Axes: Colored plot object.
        """
        ax.pcolormesh(
            self.extended_angular_coordinates,
            self.extended_radial_coordinates,
            interpolated_segment_values.T,
            cmap=self.cmap,
            norm=self.norm,
        )

        return ax
