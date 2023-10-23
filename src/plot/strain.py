from matplotlib import colors, pyplot, ticker
from numpy.typing import NDArray

from parameters.parameters import BIOMARKER_FEATURES
from plot import biomarker


class Strain(biomarker.Biomarker):
    """Class for coloring the AHA plot with strain values"""

    @property
    def biomarker_name(self) -> str:
        return "strain"

    @property
    def norm(self) -> colors.BoundaryNorm:
        norm = colors.BoundaryNorm(self.levels, ncolors=self.cmap.N, clip=True)
        return norm

    @property
    def levels(self) -> ticker.MaxNLocator:
        nbins = BIOMARKER_FEATURES[self.biomarker_name]["n_bins"]
        tick_values = BIOMARKER_FEATURES[self.biomarker_name]["tick_values"]
        return ticker.MaxNLocator(nbins=nbins).tick_values(**tick_values)

    @biomarker.validate_resolution
    def color_plot(self, ax: pyplot.Axes, interpolated_segment_values: NDArray) -> pyplot.Axes:
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
