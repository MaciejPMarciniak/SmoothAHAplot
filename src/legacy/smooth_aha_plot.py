from typing import Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

from src import aha_interpolation
from src.parameters import parameters
from utils.plot_style import PlotStyle, PlotUtil


class AHAPlotting:
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

    def __init__(self, values: list[int], plot_output_path: str = ""):
        self._segment_values: list[int]
        self._n_segments: int
        self._output_path: str
        self._theta: np.ndarray

        self.segment_values = values
        self.output_path = plot_output_path

        self.ps = PlotStyle()
        self.pu = PlotUtil()
        if self.n_segments == 17:
            self.ip = parameters.AHA17Parameters()
        else:
            self.ip = parameters.AHA18Parameters()

        self.theta = np.linspace(0, 2 * np.pi, self.ip.resolution[0])

        ai = aha_interpolation.AHAInterpolation(self.segment_values)
        self._interpolated_segment_values: np.ndarray = ai.interpolate_aha_values()

        self.fig, self.ax = plt.subplots(
            figsize=(12, 8), nrows=1, ncols=1, subplot_kw={"projection": "polar"}
        )
        self.levels = None

    @property
    def segment_values(self) -> list[int]:
        return self._segment_values

    @segment_values.setter
    def segment_values(self, values: list[int]):
        self._n_segments = len(values)
        self._segment_values = values

    @property
    def n_segments(self):
        return self._n_segments

    @property
    def theta(self) -> np.ndarray:
        return self._theta

    @theta.setter
    def theta(self, angles: np.ndarray):
        assert len(angles) == self.ip.resolution[0], (
            "Number of provided angle values {len(angles)} does not match the"
            " desired resolution (self.ip.resolution[0]}"
        )
        self._theta = angles

    @property
    def interpolated_segment_values(self):
        return self._interpolated_segment_values

    # def _write_segment_names(self):
    #     for wall in range(len(parameters.AHA_SEGMENT_NAMES["walls"])):
    #         segment_name_direction = np.deg2rad(
    #             self.pu.annotation_shift_functions[len(parameters.AHA_SEGMENT_NAMES["walls"])](wall)
    #         )
    #         segment_name_position = (
    #             self.ip.radial_position[-1]
    #             + self.ps.positional_parameters["segment_names_position"]
    #         )
    #         segment_name = parameters.AHA_SEGMENT_NAMES["walls"][wall]
    #         segment_name_orientation = self.ps.positional_parameters["segment_name_orientations"][
    #             wall
    #         ]

    #         self.ax.text(
    #             x=segment_name_direction,
    #             y=segment_name_position,
    #             s=segment_name,
    #             rotation=segment_name_orientation,
    #             **self.ps.segment_name_style,
    #         )

    # def _draw_radial_bounds(self):
    #     for radial_bound in range(self.ps.aha_bounds[self.n_segments].shape[0]):
    #         self.ax.plot(
    #             self.theta,
    #             np.repeat(self.ps.aha_bounds[self.n_segments][radial_bound], self.theta.shape),
    #             **self.ps.segment_border_style,
    #         )

    # def _draw_bounds(self, inner: float, outer: float, n_borders: int):
    #     assert 0 <= inner <= 1, f"Inner starting point value must be between 0 and 1 (is {inner})"
    #     assert 0 <= outer <= 1, f"Outer starting point value must be between 0 and 1 (is {outer})"
    #     assert inner < outer, f"Inner ({inner}) cannot be greater than outer ({outer})"
    #     assert n_borders in (4, 6), (
    #         f"Only 4 or 6 borders between segments are allowed ({n_borders} " f"provided)"
    #     )

    #     shift_function = self.pu.border_shift_functions[n_borders]

    #     for segment_border in range(n_borders):
    #         border_orientation = np.deg2rad(shift_function(segment_border))
    #         self.ax.plot(
    #             [border_orientation, border_orientation],
    #             [inner, outer],
    #             **self.ps.segment_border_style,
    #         )

    # def _draw_outer_bounds(self):
    #     self._draw_bounds(self.ps.aha_bounds[self._n_segments][1], 1, 6)

    # def _draw_inner_bounds(self):
    #     if self._n_segments == 17:
    #         self._draw_bounds(
    #             self.ps.aha_bounds[self._n_segments][0], self.ps.aha_bounds[self._n_segments][1], 4
    #         )
    #     else:
    #         self._draw_bounds(0, self.ps.aha_bounds[self._n_segments][1], 6)

    # def _draw_aha_bounds(self):
    #     self._draw_radial_bounds()
    #     self._draw_outer_bounds()
    #     self._draw_inner_bounds()

    # TODO: Create interactive widget

    # def _annotate_segment(self, angle: float, position: float, value: Union[int, float]):
    #     self.ax.text(angle, position, value, **self.ps.values_style)

    # @staticmethod
    # def _fix_negative_zero(value: Union[float, int]):
    #     return 0 if np.abs(np.round(value, 1)) < 0.1 else int(value)

    # def _get_annotation_angle(self, n_level_segments: int, segment: int):
    #     return np.deg2rad(self.pu.annotation_shift_functions[n_level_segments](segment))

    # def _annotate_basal_segments(self):
    #     n_level_segments = len(parameters.AHA_SEGMENT_NAMES["walls"])
    #     for segment in range(n_level_segments):
    #         angle = self._get_annotation_angle(n_level_segments, segment)
    #         position = float(
    #             np.mean(
    #                 [
    #                     self.ps.aha_bounds[self.n_segments][-2],
    #                     self.ps.aha_bounds[self.n_segments][-1],
    #                 ]
    #             )
    #         )
    #         value = self._fix_negative_zero(self.segment_values[segment])
    #         self._annotate_segment(angle, position, value)

    # def _annotate_mid_segments(self):
    #     n_level_segments = len(parameters.AHA_SEGMENT_NAMES["walls"])
    #     for segment in range(n_level_segments):
    #         angle = self._get_annotation_angle(n_level_segments, segment)
    #         position = float(
    #             np.mean(
    #                 [
    #                     self.ps.aha_bounds[self.n_segments][-3],
    #                     self.ps.aha_bounds[self.n_segments][-2],
    #                 ]
    #             )
    #         )
    #         value = self._fix_negative_zero(self.segment_values[segment + 6])
    #         self._annotate_segment(angle, position, value)

    # def _annotate_apical_segments(self):
    #     if self._n_segments == 17:
    #         n_level_segments = 4
    #         for segment in range(n_level_segments):
    #             angle = self._get_annotation_angle(n_level_segments, segment)
    #             position = float(
    #                 np.mean(
    #                     [
    #                         self.ps.aha_bounds[self.n_segments][0],
    #                         self.ps.aha_bounds[self.n_segments][1],
    #                     ]
    #                 )
    #             )
    #             value = self._fix_negative_zero(self.segment_values[segment + 12])
    #             self._annotate_segment(angle, position, value)

    #         angle = position = 0
    #         value = self._fix_negative_zero(self.segment_values[-1])
    #         self._annotate_segment(angle, position, value)
    #     else:
    #         n_level_segments = len(parameters.AHA_SEGMENT_NAMES["walls"])
    #         for segment in range(n_level_segments):
    #             angle = self._get_annotation_angle(n_level_segments, segment)
    #             position = self.ip.apical_position
    #             value = self._fix_negative_zero(self.segment_values[segment + 12])
    #             self._annotate_segment(angle, position, value)

    # def _annotate_aha_segments(self):
    #     self._annotate_basal_segments()
    #     self._annotate_mid_segments()
    #     self._annotate_apical_segments()

    def bullseye_smooth(
        self,
        cmap: str = "jet",
        norm: Union[BoundaryNorm, tuple[int, int]] | None = None,
        title: str = "Smooth AHA plot",
        smooth_contour: bool = False,
        units: str = "",
        add_colorbar: bool = True,
    ):
        """
        Function to create the smooth representation of the AHA 17 segment plot
        :param cmap: ColorMap or None, optional
            Set the desired colormap
        :param norm: tuple, BoundaryNorm or None
            Tuple (vmin, vmax) - normalize data into the [0.0, 1.0] range with desired values.
        :param units: str
            Label of the color bar
        :param title: str
            Title of the plot
        :param smooth_contour: Bool
            Whether to smooth the plot. Useful for level-based color map
        :param add_colorbar: Bool
            Whether to add color bar with the scale on the side of the plot
        :return fig: matplotlib.pyplot.figure
            The figure on which the 17 AHA plot has been drawn
        """

        self._draw_aha_bounds()
        self._write_segment_names()
        self._clear_bullseye_plot()

        normalized_data = self._normalize_data(norm)
        self._color_plot(cmap, normalized_data, smooth_contour)
        if add_colorbar:
            self._add_color_bar(units, cmap, normalized_data)

        self._annotate_aha_segments()

        self.ax.set_title(title, fontsize=24, pad=40)

        return self.fig
