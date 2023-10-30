import matplotlib.pyplot as plt

from aha import aha_annotation, aha_segmental_values
from aha.parameters.parameters import PLOT_COMPONENTS
from aha.plot import bounds, plotting


class AHA:
    """
    Class for producing smooth 17 and 18 segment left ventricle plot, recommended by American Heart
    Association:
        http://www.pmod.com/files/download/v34/doc/pcardp/3615.htm
    Inspired with the 'bullseye plot':
        https://matplotlib.org/gallery/specialty_plots/leftventricle_bulleye.html
    Available at:
        https://github.com/MaciejPMarciniak/smoothAHAplot

    Two methods are included, adjusted to plot myocardial work and strain values with proper scales.
    """

    def __init__(
        self,
        segments: dict[str, float],
        plot_type: str,
        plot_output_path: str = "",
    ):
        self._segments = aha_segmental_values.AHASegmentalValues(segments=segments)
        self._plot_type = plot_type
        self._output_path = plot_output_path
        self.fig = plt.Figure
        self.ax = plt.Axes

    @property
    def segment_values(self) -> list[int]:
        return self.segments.segmental_values

    @property
    def segments(self) -> aha_segmental_values.AHASegmentalValues:
        return self._segments

    def bullseye_smooth(
        self,
        add_colorbar: bool = True,
    ) -> plt.Figure:
        """
        Function to create the smooth representation of the AHA 17 segment plot
        :param add_colorbar: Bool
            Whether to add color bar with the scale on the side of the plot
        :return fig: matplotlib.pyplot.figure
            The figure on which the 17 AHA plot has been drawn
        """

        self.fig, self.ax = plt.subplots(
            figsize=PLOT_COMPONENTS["figure_size"],
            nrows=1,
            ncols=1,
            subplot_kw={"projection": "polar"},
            layout="constrained",
        )

        ax_annotation = aha_annotation.AHAAnnotation(segments=self.segments, ax=self.ax)
        self.ax = ax_annotation.annotate_aha_segments()
        ax_bounds = bounds.AHAPlotBounds(len(self.segments), ax=self.ax)
        self.ax = ax_bounds.draw_aha_bounds()
        ax_plotting = plotting.AHAPlotting(ax=self.ax, fig=self.fig, biomarker_name=self._plot_type)
        ax_plotting.create_plot(self.segments)
        if add_colorbar:
            ax_plotting.add_color_bar()
        return self.fig
