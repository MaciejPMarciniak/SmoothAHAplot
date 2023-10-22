import numpy as np
from matplotlib import colors, pyplot

from src.coloring import biomarker
from src.parameters.parameters import BIOMARKER_FEATURES


class MyocardialWork(biomarker.Biomarker):
    """Class for coloring the AHA plot with myocardial work values"""

    @property
    def feature(self) -> str:
        return "myocardial_work"

    @property
    def norm(self) -> tuple[int, int]:
        norm = tuple(BIOMARKER_FEATURES[self.feature]["norm"])
        normalized_norm = colors.Normalize(vmin=norm[0], vmax=norm[1])
        return normalized_norm

    @property
    def units(self) -> str:
        return "mmHg%"

    @biomarker.validate_resolution
    def color_plot(self, ax: pyplot.Axes, interpolated_segment_values: np.array) -> pyplot.Axes:
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
