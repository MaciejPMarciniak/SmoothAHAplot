import numpy as np
from matplotlib import colors, pyplot, ticker

from src.coloring import biomarker
from src.parameters.parameters import BIOMARKER_FEATURES


class Strain(biomarker.Biomarker):
    """Class for coloring the AHA plot with strain values"""

    @property
    def feature(self) -> str:
        return "strain"

    @property
    def norm(self) -> colors.BoundaryNorm:
        norm = colors.BoundaryNorm(self.levels, ncolors=self.cmap.N, clip=True)
        return norm

    @property
    def units(self) -> str:
        return "%"

    @property
    def levels(self) -> ticker.MaxNLocator:
        nbins = BIOMARKER_FEATURES[self.feature]["n_bins"]
        tick_values = BIOMARKER_FEATURES[self.feature]["tick_values"]
        return ticker.MaxNLocator(nbins=nbins).tick_values(**tick_values)

    @biomarker.validate_resolution
    def color_plot(self, ax: pyplot.Axes, interpolated_segment_values: np.array) -> pyplot.Axes:
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
