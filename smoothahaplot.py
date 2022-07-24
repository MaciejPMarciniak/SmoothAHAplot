import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pef
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

import parameters
from plot_style import PlotStyle
from wt_from_ex_files import ExNodeParser

from typing import List, Dict


def confirm_segment_number(func):
    def inner(self, *args, **kwargs):
        if not (len(self._n_segments) == 17 or len(self._n_segments) == 18):
            raise SegmentSizeError(
                f'Incorrect number of segment values provided: {len(self._n_segments)}. Provide either '
                f'17 or 18 segment values')
        func(self, *args, **kwargs)

    return inner


class AHASegmentalValues:

    def __init__(self, segments: pd.Series | Dict):
        self._segments = None
        self._n_segments = 0
        self.segments = segments
        self._segmental_values = []
        self._get_segmental_values()

    @property
    def segments(self):
        return self._segments

    @segments.setter
    def segments(self, new_segments: List[int]):
        if not (len(new_segments) == 17 or len(new_segments) == 18):
            raise SegmentSizeError(f'Incorrect number of segment values provided: {len(new_segments)}. Provide either '
                                   f'17 or 18 segment values')
        self._segments = new_segments
        self._n_segments = len(self._segments)

    @confirm_segment_number
    def _extract_values_from_dict(self):

        for segment_name in parameters.AHA_SEGMENT_NAMES[self._n_segments]:
            try:
                self._segmental_values.append(self.segments[segment_name])
            except KeyError:
                exit('Value of segment {} is missing. Provide values for all AHA 17/18 segments'.format(segment_name))

    @confirm_segment_number
    def _extract_values_from_series(self):

        segments_s = self.segments.reindex(parameters.AHA_SEGMENT_NAMES(self._n_segments), axis=1)
        if segments_s.isnull().values.any():
            exit('Segmental names are incompatibile:\n{}\n{}'.format(segments_s.index,
                                                                     parameters.AHA_SEGMENT_NAMES(self._n_segments)))
        self._segmental_values = segments_s.values

    @confirm_segment_number
    def _get_segmental_values(self):

        if isinstance(self.segments, dict):
            self._extract_values_from_dict()
        elif isinstance(self.segments, pd.Series):
            self._extract_values_from_series()
        else:
            raise SegmentsError(f'Unknown format of the segment list provided: {type(self.segments)}')


class AHAInterpolation:

    def __init__(self, segmental_values: List[int]):
        self._segmental_values = None
        self._n_segments = 0
        self.interpolated_values = None

        self.segmental_values = segmental_values
        self.ip = self._assign_interpolation_parameters()

    @property
    def segmental_values(self):
        return self._segmental_values

    @segmental_values.setter
    def segmental_values(self, new_values: List[int]):
        if not (len(new_values) == 17 or len(new_values) == 18):
            raise SegmentSizeError(f'Incorrect number of segment values provided: {len(new_values)}. Provide either '
                                   f'17 or 18 segment values')
        self._segmental_values = new_values
        self._n_segments = len(self._segmental_values)

    def _assign_interpolation_parameters(self) -> parameters.InterpolationParameters:
        if self._n_segments == 17:
            return parameters.AHA17Parameters()
        return parameters.AHA18Parameters()

    def _interpolate_directions(self, regional_values: List[int]) -> np.ndarray:
        res = self.ip.resolution[0]
        n_segments = len(regional_values)
        interpolated_array = np.zeros(self.ip.resolution[0])

        for i in range(n_segments):
            interpolated_array[int(res / n_segments) * i:int(res / n_segments * i + res / n_segments)] = \
                np.linspace(regional_values[i], regional_values[(i + 1) % n_segments], int(res / n_segments))

        return interpolated_array

    @staticmethod
    def basal_mid(basal: np.ndarray, mid: np.ndarray) -> np.ndarray:
        """
        :return: Helper array for better basal segments visualization
        """
        return (basal * 3 + mid) / 4

    @confirm_segment_number
    def _interpolate_17_aha_values_along_circle(self):
        """
        Interpolate the initial 17 values, to achieve smooth transition among segments.
        """
        basal = self._interpolate_directions(self.segmental_values[:6])
        mid = self._interpolate_directions(self.segmental_values[6:12])
        apex_mid = self._interpolate_directions(self.segmental_values[12:16])
        apex = np.repeat(self.segmental_values[16], self.ip.resolution[0])
        return basal, mid, apex_mid, apex

    @confirm_segment_number
    def _interpolate_18_aha_values_along_circle(self):
        """
        Interpolate the initial 18 values, to achieve smooth transition among segments.
        """
        basal = self._interpolate_directions(self.segmental_values[:6])
        mid = self._interpolate_directions(self.segmental_values[6:12])
        apex_mid = self._interpolate_directions(self.segmental_values[12:])
        apex = np.repeat(np.sum(self.segmental_values[12:]) / 6, self.ip.resolution[0])
        return basal, mid, apex_mid, apex

    @confirm_segment_number
    def interpolate_aha_values(self):
        if self._n_segments == 17:
            interp_func = self._interpolate_17_aha_values_along_circle
        else:
            interp_func = self._interpolate_18_aha_values_along_circle

        # Set up the circular interpolation matrices
        basal, mid, apex_mid, apex = interp_func()
        along_x = np.array([basal, self.basal_mid(basal, mid), mid, apex_mid, apex])

        # Adjust to visualisation
        along_x = np.roll(along_x, int(self.ip.resolution[0] / 4), axis=1)
        along_x = np.flip(along_x, 0)

        # Interpolate along the radius
        f = interp1d(self.ip.plot_levels, along_x, axis=0)
        along_x_y = f(np.linspace(0, 1, self.ip.resolution[1]))

        return along_x_y


class AHAPlotting:
    """
    Class for producing smooth 17 and 18 segment left ventricle plot, recommended by American Heart Association:
        http://www.pmod.com/files/download/v34/doc/pcardp/3615.htm
    Inspired with the 'bullseye plot':
        https://matplotlib.org/gallery/specialty_plots/leftventricle_bulleye.html
    Available at:
        https://github.com/MaciejPMarciniak/smoothAHAplot

    Two helper methods are included, adjusted to plot myocardial work and strain values with proper scales.
    """

    def __init__(self, segments, output_path=''):

        self.aha_interpolation = AHAInterpolation(segments)
        self.output_path = output_path
        self.levels = None
        self.fig = None
        self.ps = PlotStyle()

    def _draw_interpolation_positions(self, ax):

        for i in range(8):
            theta_i = np.deg2rad(i * 45)
            ax.plot([theta_i, theta_i], [0, 1], '--', c='gray')

        for i in range(360):
            theta_i = np.deg2rad(i)
            theta_i_roll = theta_i + np.deg2rad(1)
            mesh_nodes = [0, 0.1, 0.25, 0.4, 0.5, 0.63, 0.75, 0.87, 1]
            for m_node in mesh_nodes:
                color_ = 'b' if m_node in [0.87, 1] else \
                    'g' if m_node == 0.75 else \
                        'y' if m_node in [0.5, 0.63] else \
                            'r' if m_node in [0.25, 0.4] else 'k'

                ax.plot([theta_i, theta_i_roll], [m_node, m_node], ':', c=color_, lw=5)
                plt.show()

    def bullseye_17_smooth(self, fig, ax, cmap='jet', color_seg_names=False, norm=None, units='Units',
                           title='Smooth 17 AHA plot', smooth_contour=False, echop=False, draw_interpolation=False):
        """
        Function to create the smooth representation of the AHA 17 segment plot
        :param fig: matplotlib.pyplot.figure
            The plot is drawn on this figure
        :param ax: matplotlib.pyplot.axes
            Axes of the figure, for 17 AHA and colorbar.
        :param cmap: ColorMap or None, optional
            Optional argument to set the desired colormap
        :param color_seg_names: boolean, default - False
            Whether or not to color the segment names with traditional echocardiography colors
        :param norm: tuple, BoundaryNorm or None
            Tuple (vmin, vmax) - normalize data into the [0.0, 1.0] range with minimum and maximum desired values.
        :param units: str
            Label of the color bar
        :param title: str
            Title of the plot
        :param smooth_contour: Bool
            Whether to smooth the plot. Useful for level-based color map
        :param echop: Bool
            If true, the resultant plot is structured as the 17 AHA plots in GE EchoPAC (TM)
        :param draw_interpolation: Bool
            Whether to draw interpolation lines on the plot
        :return fig: matplotlib.pyplot.figure
            The figure on which the 17 AHA plot has been drawn
        """

        if norm is None:
            norm = mpl.colors.Normalize(vmin=self.seg_values.min(), vmax=self.seg_values.max())
        elif isinstance(norm, tuple) and len(norm) == 2:
            norm = mpl.colors.Normalize(vmin=norm[0], vmax=norm[1])
        else:
            pass

        if echop:
            rot = [0, 0, 0, 0, 0, 0]
            seg_align_12 = 30
            seg_align_13_16 = [40, 50, 40, 50]
            seg_names = parameters.ECHOPAC_SEGMENT_NAMES
            seg_names_pos = [0.1, 0.06, 0.1, 0.1, 0.06, 0.1]
        else:
            rot = [0, 60, -60, 0, 60, -60]
            seg_align_12 = 90
            seg_align_13_16 = np.repeat([90], 4)
            seg_names = [col_name.split(' ')[1] for col_name in parameters.AHA_17_SEGMENT_NAMES[:6]]
            seg_names_pos = np.repeat([0.06], 6)

        # -----Basic assumptions on resolution--------------------------------------------------------------------------
        self.seg_values = np.array(self.seg_values).ravel()
        theta = np.linspace(0, 2 * np.pi, self.ip.resolution[0])
        if echop:
            theta -= np.pi / 3
        r = np.linspace(0.2, 1, 4)
        # ==============================================================================================================

        # -----Drawing bounds of the plot-------------------------------------------------------------------------------
        linewidth = 2

        # Create the radial bounds
        for i in range(r.shape[0]):
            ax.plot(theta, np.repeat(r[i], theta.shape), '-k', lw=linewidth)

        # Create the bounds for the segments 1-12
        for i in range(6):
            theta_i = np.deg2rad(i * 60)
            ax.plot([theta_i, theta_i], [r[1], 1], '-k', lw=linewidth)

        # Create the bounds for the segments 13-16
        for i in range(4):
            theta_i = np.deg2rad(i * 90 - 45)
            if echop:
                theta_i += np.pi / 4
            ax.plot([theta_i, theta_i], [r[0], r[1]], '-k', lw=linewidth)

        # Clear the bullseye plot
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_ylim([0, 1])
        if draw_interpolation:
            self._draw_interpolation_positions(ax)
        # ==============================================================================================================

        # -----Linear interpolation-------------------------------------------------------------------------------------
        if len(self.seg_values) == 17:
            interp_data = self._interpolate_17_aha_values(self.seg_values)
        elif len(self.seg_values) == 18:
            interp_data = self._interpolate_18_aha_values(self.seg_values)
        else:
            exit('Wrong number of segments provided: {}'.format(len(self.seg_values)))
            return -1

        r = np.linspace(0, 1, interp_data.shape[0])
        float_values = False
        # ==============================================================================================================

        # -----Fill segments -------------------------------------------------------------------------------------------
        r0 = np.repeat(r[:, np.newaxis], self.ip.resolution[0], axis=1).T
        theta0 = np.repeat(theta[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data
        z = z.T

        # Color the plot
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0, r0, z, cmap=cmap, levels=self.levels)
            cf.ax.axis('off')
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)

        # Annotate
        for i in range(6):
            # Segments 1-6
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[73:]),  # position (circumferential, norm)
                    0 if np.abs(np.round(self.seg_values[i], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i]),  # values
                    **self.ps.values_style)
            # Segments 7-12
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[46:73]),
                    0 if np.abs(np.round(self.seg_values[i + 6], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i + 6]),  # values
                    **self.ps.values_style)
            # Segment names
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i], weight='bold' if color_seg_names else None,
                    color=self.ps.segment_name_colors[i] if color_seg_names else 'k',
                    path_effects=[pef.Stroke(linewidth=1, foreground='k'), pef.Normal()] if color_seg_names else None)
        # Segments 13-16
        for i in range(4):
            ax.text(np.deg2rad(i * 90) + np.deg2rad(seg_align_13_16[i]), np.mean(r[20:46]),
                    0 if np.abs(np.round(self.seg_values[i + 12], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i + 12]),  # values
                    **self.ps.values_style)
        # Segment 17
        ax.text(0, 0,
                0 if np.abs(np.round(self.seg_values[16], 1)) < 0.1 else
                int(self.seg_values[16]),  # value
                **self.ps.values_style)
        # ==============================================================================================================

        # -----Add plot features-----------------------------------------v----------------------------------------------
        # Create the axis for the colorbars
        bar = fig.add_axes([0.05, 0.1, 0.2, 0.05])
        cb1 = mpl.colorbar.ColorbarBase(bar, cmap=cmap, norm=norm, orientation='horizontal')
        cb1.set_label(units, size=16)
        cb1.ax.tick_params(labelsize=14, which='major')

        ax.set_title(title, fontsize=24)
        # ==============================================================================================================

        return fig

    def bullseye_18_smooth(self, fig, ax, cmap='jet', color_seg_names=False, norm=None, units='Units',
                           title='Smooth 18 AHA plot', smooth_contour=False, echop=False):
        """
        Function to create the smooth representation of the AHA 18 segment plot
        :param fig: matplotlib.pyplot.figure
            The plot is drawn on this figure
        :param ax: matplotlib.pyplot.axes
            Axes of the figure, for 18 AHA and colorbar.
        :param cmap: ColorMap or None, optional
            Optional argument to set the desired colormap
        :param color_seg_names: boolean, default - False
            Whether or not to color the segment names with traditional echocardiography colors
        :param norm: tuple, BoundaryNorm or None
            Tuple (vmin, vmax) - normalize data into the [0.0, 1.0] range with minimum and maximum desired values.
        :param units: str
            Label of the color bar
        :param title: str
            Title of the plot
        :param smooth_contour:
            Whether to smooth the plot. Useful for level-based color map
        :param echop: Bool
            If true, the resultant plot is structured as the 18 AHA plots in GE EchoPAC (TM)
        :return fig: matplotlib.pyplot.figure
            The figure on which the 18 AHA plot has been drawn
        """

        if norm is None:
            norm = mpl.colors.Normalize(vmin=self.seg_values.min(), vmax=self.seg_values.max())
        elif isinstance(norm, tuple) and len(norm) == 2:
            norm = mpl.colors.Normalize(vmin=norm[0], vmax=norm[1])
        else:
            pass

        if echop:
            rot = [0, 0, 0, 0, 0, 0]
            seg_align = 30
            seg_names = parameters.ECHOPAC_SEGMENT_NAMES
            seg_names_pos = [0.1, 0.06, 0.1, 0.1, 0.06, 0.1]
        else:
            rot = [0, 60, -60, 0, 60, -60]
            seg_align = 90
            seg_names = parameters.AHA_SEGMENT_NAMES
            seg_names_pos = np.repeat([0.06], 6)

        # -----Basic assumptions on resolution--------------------------------------------------------------------------
        self.seg_values = np.array(self.seg_values).ravel()
        theta = np.linspace(0, 2 * np.pi, self.ip.resolution[0])
        if echop:
            theta -= np.pi / 3
        r = np.linspace(0.38, 1, 3)
        # ==============================================================================================================

        # -----Drawing bounds of the plot-------------------------------------------------------------------------------
        linewidth = 2
        # Create the radial bounds
        for i in range(r.shape[0]):
            ax.plot(theta, np.repeat(r[i], theta.shape), '-k', lw=linewidth)

        # Create the bounds for the segments 1-18
        for i in range(6):
            theta_i = np.deg2rad(i * 60)
            ax.plot([theta_i, theta_i], [0, 1], '-k', lw=linewidth)
        # ==============================================================================================================

        # -----Linear interpolation-------------------------------------------------------------------------------------
        if len(self.seg_values) == 17:
            interp_data = self._interpolate_17_aha_values(self.seg_values)
        elif len(self.seg_values) == 18:
            interp_data = self._interpolate_18_aha_values(self.seg_values)
        else:
            exit('Wrong number of segments provided: {}'.format(len(self.seg_values)))
            return -1

        r = np.linspace(0, 1, interp_data.shape[0])
        # ==============================================================================================================

        # -----Fill segments 1:18---------------------------------------------------------------------------------------
        r0 = r
        r0 = np.repeat(r0[:, np.newaxis], self.ip.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data
        z = z.T

        # Annotate
        for i in range(6):
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.84,
                    0 if np.abs(np.round(self.seg_values[i], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i]),
                    **self.ps.values_style)
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.55,
                    0 if np.abs(np.round(self.seg_values[i + 6], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i + 6]),
                    **self.ps.values_style)
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.25,
                    0 if np.abs(np.round(self.seg_values[i + 12], 1)) < 0.1 else  # condition to not allow 'negative 0'
                    int(self.seg_values[i + 12]),
                    **self.ps.values_style)
            # Segment names
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i],
                    color=self.ps.segment_name_colors[i] if color_seg_names else 'k',
                    path_effects=[pef.Stroke(linewidth=1, foreground='k'), pef.Normal()] if color_seg_names else None)
        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0, r0, z, cmap=cmap, levels=self.levels)
            cf.ax.axis('off')
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)
        # ==============================================================================================================

        # -----Add plot featres-----------------------------------------------------------------------------------------
        # Create the axis for the colorbars
        bar = fig.add_axes([0.05, 0.1, 0.2, 0.05])
        cb1 = mpl.colorbar.ColorbarBase(bar, cmap=cmap, norm=norm, orientation='horizontal')
        cb1.set_label(units, size=16)
        cb1.ax.tick_params(labelsize=14, which='major')

        # Clear the bullseye plot
        ax.set_ylim([0, 1])
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_title(title, fontsize=24)
        # ==============================================================================================================

        return fig

    def _plot_setup(self, data):

        if data is not None:
            assert len(data) == self.n_segments, 'Please provide correct number of segmental values for the plot. ' \
                                                 'len(data) = {}, n_segments =  {}'.format(len(data), self.n_segments)
            if not isinstance(data, list):
                data = self._get_segmental_values(data)

        return data

    def plot_myocardial_work(self, filename='', data=None, echop=False):

        self.seg_values = self._plot_setup(data)

        cmap = plt.get_cmap('rainbow')
        norm = (1000, 3000)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1,
                               subplot_kw=dict(projection='polar'))
        if self.n_segments == 18:
            fig = self.bullseye_18_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Myocardial work index',
                                          units='mmHg%', smooth_contour=False, echop=echop)
        else:
            fig = self.bullseye_17_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Myocardial work index',
                                          units='mmHg%', smooth_contour=False, echop=echop)
        fig.savefig(os.path.join(self.output_path, filename))

    def plot_strain(self, filename='', data=None, echop=False):

        self.seg_values = self._plot_setup(data)

        self.levels = MaxNLocator(nbins=12).tick_values(-30, 30)
        cmap = plt.get_cmap('seismic_r')
        norm = BoundaryNorm(self.levels, ncolors=cmap.N, clip=True)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1, subplot_kw=dict(projection='polar'))
        if self.n_segments == 18:
            fig = self.bullseye_18_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Longitudinal strain', units='%',
                                          smooth_contour=True, echop=echop)
        else:
            fig = self.bullseye_17_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Longitudinal strain', units='%',
                                          smooth_contour=True, echop=echop)
        fig.savefig(os.path.join(self.output_path, filename))

    def plot_wall_thickness(self, filename='', data=None, echop=False):

        if data is not None:
            self.seg_values = data

        cmap = plt.get_cmap('RdYlBu_r')
        norm = (4, 10)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1, subplot_kw=dict(projection='polar'))
        if self.n_segments == 18:
            fig = self.bullseye_18_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness',
                                          units='mm', smooth_contour=False, echop=echop)
        else:
            fig = self.bullseye_17_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness',
                                          units='mm', smooth_contour=False, echop=echop)
        fig.savefig(os.path.join(self.output_path, filename))

    def plot_wt_difference(self, filename='', data=None, echop=False):

        if data is not None:
            self.seg_values = data

        cmap = plt.get_cmap('coolwarm')
        norm = (-2.0, 2.0)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1, subplot_kw=dict(projection='polar'))
        if self.n_segments == 18:
            fig = self.bullseye_18_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness difference',
                                          units='mm', smooth_contour=False, echop=echop)
        else:
            fig = self.bullseye_17_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness difference',
                                          units='mm', smooth_contour=False, echop=echop)
        fig.savefig(os.path.join(self.output_path, filename))


class SegmentsError(AttributeError):
    """An error related to AHA segments"""


class SegmentSizeError(SegmentsError):
    """An error related to number of segments"""


if __name__ == '__main__':
    group_a = 2
    scale = 72
    exnode1 = r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime\MeanEigen{}Scale{}.exnode'.format(group_a, scale)
    exnode2 = r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime\MeanEigen{}Scalen{}.exnode'.format(group_a, scale)
    wt = ExNodeParser(exnode1, r'G:')
    wt.calc_wall_thickness()
    wt2 = ExNodeParser(exnode2, r'C:')
    wt2.calc_wall_thickness()
    wt_diff = wt.wt_difference(exnode2)
    plot_wt = SmoothAHAPlot(wt.wall_thicknesses, r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime', n_segments=17)
    plot_wt.plot_wall_thickness(filename='WT_plot_{}_pos'.format(group_a))

    #
    plot_wt = SmoothAHAPlot(wt_diff, r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime', n_segments=17)
    plot_wt.plot_wt_difference(filename='WT_pos_neg_difference_mode_{}'.format(group_a))
    plot_wt = SmoothAHAPlot(wt2.wall_thicknesses, r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime', n_segments=17)
    plot_wt.plot_wall_thickness(filename='WT_plot_{}_neg'.format(group_a))