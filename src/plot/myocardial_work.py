from matplotlib import colors, pyplot
from numpy.typing import NDArray

from parameters.parameters import BIOMARKER_FEATURES
from plot import biomarker


class MyocardialWork(biomarker.Biomarker):
    """Class for coloring the AHA plot with myocardial work values"""

    @property
    def biomarker_name(self) -> str:
        return "myocardial_work"

    @property
    def norm(self) -> tuple[int, int]:
        norm = tuple(BIOMARKER_FEATURES[self.biomarker_name]["norm"])
        normalized_norm = colors.Normalize(vmin=norm[0], vmax=norm[1])
        return normalized_norm

    @biomarker.validate_resolution
    def color_plot(self, ax: pyplot.Axes, interpolated_segment_values: NDArray) -> pyplot.Axes:
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
