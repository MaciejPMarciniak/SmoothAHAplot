import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pef
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


class SmoothAHAPlot:
    """
    Class for producing smooth 17 and 18 segment left ventricle plot, recommended by American Heart Association:
        http://www.pmod.com/files/download/v34/doc/pcardp/3615.htm
    Inspired with the 'bullseye plot':
        https://matplotlib.org/gallery/specialty_plots/leftventricle_bulleye.html
    Available at:
        https://github.com/MaciejPMarciniak/smoothAHAplot

    Two helper methods are included, adjusted to plot myocardial work and strain values with proper scales.
    """

    # If pandas Series/dictionary must have following index/keys:
    AHA_17_SEGMENT_NAMES = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
                            'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
                            'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
                            'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
                            'Apical Anterior', 'Apical Septal', 'Apical Inferior', 'Apical Lateral', 'Apex']
    # or
    AHA_18_SEGMENT_NAMES = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
                            'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
                            'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
                            'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
                            'Apical Anterior', 'Apical Anteroseptal', 'Apical Inferoseptal',
                            'Apical Inferior', 'Apical Inferolateral', 'Apical Anterolateral']

    # The names of the segments:
    AHA_SEGMENT_NAMES = ['Anterior', 'Anteroseptal', 'Inferoseptal',
                         'Inferior', 'Inferolateral', 'Anterolateral']

    # EchoPAC version of the names:
    ECHOP_SEGMENT_ABBRV = ['ANT', 'ANT_SEPT', 'SEPT', 'INF', 'POST', 'LAT']

    COLORS = ['cyan', 'yellow', 'red', 'blue', 'magenta', 'green']

    def __init__(self, segments, output_path='', n_segments=None):

        assert n_segments in [17, 18], ('Please provide the correct number of points for the plot: 17, 18 or 65.'
                                          'Current n_points: {}'.format(n_segments))
        self.n_segments = n_segments

        if segments is None:
            self.seg_values = [0] * n_segments
            print('No data provided. Please provide segmental values for the plot: SmoothAHAPlot.data = ...')
        else:
            assert len(segments) in [n_segments, 65], 'Please provide the proper number of segmental values for the' \
                                                'plot. len(data) = {}, n_segments: {}'.format(len(segments), n_segments)
            self.seg_values = self._get_segmental_values(segments)

        self.output_path = output_path
        self.levels = None
        self.fig = None
        self.resolution = (768, 100)

    def _get_segmental_values(self, segments):

        if len(segments) == 65:
            return segments

        if self.n_segments == 17:
            seg_list = self.AHA_17_SEGMENT_NAMES
        elif self.n_segments == 18:
            seg_list = self.AHA_18_SEGMENT_NAMES

        segmental_values = []
        if isinstance(segments, dict):
            for seg_name in seg_list:
                try:
                    segmental_values.append(segments[seg_name])
                except KeyError:
                    exit('Value of segment {} is missing!'.format(seg_name))

        elif isinstance(segments, pd.Series):
            segments = segments.reindex(seg_list, axis=1)
            if segments.isnull().values.any():
                exit('Segmental names are incompatibile:\n{}\n{}'.format(segments.index, seg_list))
            segmental_values = segments.values

        return segmental_values

    def _interpolate_65_to_17_values(self):

        pass


    def _interpolate_17_aha_values(self, aha_values=None):
        """
        Funtion to interpolate the initial 17 values, to achieve smooth transition among segments.
        :param aha_values: list, tuple
            The 17 values
        :return:
        """
        assert len(self.seg_values) == 17, 'Please provide the proper number of segmental values for the 17 AHA plot. ' \
                                           'len(data) = {}'.format(len(self.seg_values))
        if aha_values is None:
            aha_values = self.seg_values

        res_x = self.resolution[0]
        res_y = self.resolution[1]

        # Extract values
        basal, mid, apical, apex = aha_values[:6], aha_values[6:12], aha_values[12:16], aha_values[16]

        # Set up the interpolation matrices
        basal_interp = np.zeros(res_x)
        mid_interp = np.zeros(res_x)
        apical_interp = np.zeros(res_x)
        apex_interp = np.repeat(apex, self.resolution[0])

        # Interpolate around the radial positions
        for i in range(6):
            basal_interp[int(res_x / 6) * i:int(res_x / 6 * i + res_x / 6)] = \
                np.linspace(basal[i], basal[(i + 1) % 6], int(res_x / 6))

            mid_interp[int(res_x / 6) * i:int(res_x / 6 * i + res_x / 6)] = \
                np.linspace(mid[i], mid[(i + 1) % 6], int(res_x / 6))

        for i in range(4):
            apical_interp[int(res_x / 4) * i:int(res_x / 4 * i + res_x / 4)] = \
                np.linspace(apical[i], apical[(i + 1) % 4], int(res_x / 4))

        # Helper arrays for better basal segments visualization
        _tmp_basal = basal_interp * 3
        _tmp_mid = mid_interp
        _basal_low = (_tmp_basal + _tmp_mid) / 4

        # Put it all together
        full_map = np.array([basal_interp, _basal_low, mid_interp, apical_interp, apex_interp])
        full_map = np.roll(full_map, int(res_x/4), axis=1)
        full_map = np.flip(full_map, 0)
        y_0 = [0, 0.33, 0.55, 0.85, 1]
        f = interp1d(y_0, full_map, axis=0)
        full_map_interp = f(np.linspace(0, 1, res_y))

        return full_map_interp

    def _interpolate_18_aha_values(self, aha_values=None):
        """
        Funtion to interpolate the initial 18 values, to achieve smooth transition among segments.
        :param aha_values: list, tuple
            The 18 values
        :return:
        """
        assert len(self.seg_values) == 18, ('Please provide the proper number of segmental values for the 18 AHA plot. '
                                            'len(data) = {}'.format(len(self.seg_values)))
        if aha_values is None:
            aha_values = self.seg_values

        res_x = self.resolution[0]
        res_y = self.resolution[1]

        # Extract values
        basal, mid, apical = aha_values[:6], aha_values[6:12], aha_values[12:18]
        apex = np.sum(apical) / 6

        # Set up the interpolation matrices
        basal_interp = np.zeros(res_x)
        mid_interp = np.zeros(res_x)
        apical_interp = np.zeros(res_x)
        apex_interp = np.repeat(apex, self.resolution[0])

        # Interpolate around the radial positions
        for i in range(6):
            basal_interp[int(res_x / 6) * i:int(res_x / 6 * i + res_x / 6)] = \
                np.linspace(basal[i], basal[(i + 1) % 6], int(res_x / 6))

            mid_interp[int(res_x / 6) * i:int(res_x / 6 * i + res_x / 6)] = \
                np.linspace(mid[i], mid[(i + 1) % 6], int(res_x / 6))

            apical_interp[int(res_x / 6) * i:int(res_x / 6 * i + res_x / 6)] = \
                np.linspace(apical[i], apical[(i + 1) % 6], int(res_x / 6))

        # Helper arrays for better basal segments visualization
        _tmp_basal = basal_interp * 3
        _tmp_mid = mid_interp
        _basal_low = (_tmp_basal + _tmp_mid) / 4

        # Put it all together
        full_map = np.array([basal_interp, _basal_low, mid_interp, apical_interp, apex_interp])
        full_map = np.roll(full_map, int(res_x/4), axis=1)
        full_map = np.flip(full_map, 0)
        y_0 = [0, 0.28, 0.5, 0.8, 1]
        f = interp1d(y_0, full_map, axis=0)
        full_map_interp = f(np.linspace(0, 1, res_y))

        return full_map_interp

    def _interpolate_65_values(self, aha_values=None):
        """
        Funtion to interpolate the initial 65 values, to achieve smooth transition among segments.
        :param aha_values: list, tuple, np.array
            The 65 values
        :return:
        """
        assert len(self.seg_values) == 65, 'Please provide 65 values for the AHA plot. Number of points provided: ' \
                                           'len(data) = {}'.format(len(self.seg_values))
        if aha_values is None:
            aha_values = self.seg_values

        res_x = self.resolution[0]
        res_y = self.resolution[1]

        # Extract values
        aha_values = aha_values[::-1]
        spiral_base_to_apex = np.array(aha_values[:-1]).reshape((8, 8))

        # Set up the interpolation matrices
        spiral_interp = np.zeros((8, res_x))
        apex_interp = np.repeat(aha_values[-1], res_x)

        # Interpolate around the radial positions
        for slice_ in range(8):
            for i in range(8):
                spiral_interp[slice_, int(res_x / 8) * i:int(res_x / 8 * (i + 1))] = \
                 np.linspace(spiral_base_to_apex[slice_, i], spiral_base_to_apex[slice_, (i + 1) % 8], int(res_x / 8))

        # Put it all together
        full_map = np.append(spiral_interp, apex_interp.reshape(1, -1), axis=0)
        # full_map = np.roll(full_map, int(res_x/3), axis=1)
        full_map = np.flip(full_map, 0)

        print(full_map.shape)
        y_0 = [0, 0.04, 0.12, 0.22, 0.34, 0.5, 0.66, 0.83, 1]

        f = interp1d(y_0, full_map, axis=0)
        full_map_interp = f(np.linspace(0, 1, res_y))

        return full_map_interp

    def bullseye_17_smooth(self, fig, ax, cmap='jet', norm=None, units='Units', title='Smooth 17 AHA plot',
                           smooth_contour=False, echop=False):
        """
        Function to create the smooth representation of the AHA 17 segment plot
        :param fig: matplotlib.pyplot.figure
            The plot is drawn on this figure
        :param ax: matplotlib.pyplot.axes
            Axes of the figure, for 17 AHA and colorbar.
        :param cmap: ColorMap or None, optional
            Optional argument to set the desired colormap
        :param norm: tuple, BoundaryNorm or None
            Tuple (vmin, vmax) - normalize data into the [0.0, 1.0] range with minimum and maximum desired values.
        :param units: str
            Label of the color bar
        :param title: str
            Title of the plot
        :param smooth_contour:
            Whether to smooth the plot. Useful for level-based color map
        :param echop: Bool
            If true, the resultant plot is structured as the 17 AHA plots in GE EchoPAC (TM)
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
            seg_names = self.ECHOP_SEGMENT_ABBRV
            seg_names_pos = [0.1, 0.06, 0.1, 0.1, 0.06, 0.1]
        else:
            rot = [0, 60, -60, 0, 60, -60]
            seg_align_12 = 90
            seg_align_13_16 = np.repeat([90], 4)
            seg_names = [col_name.split(' ')[1] for col_name in self.AHA_17_SEGMENT_NAMES[:6]]
            seg_names_pos = np.repeat([0.06], 6)

        # -----Basic assumptions on resolution--------------------------------------------------------------------------
        self.seg_values = np.array(self.seg_values).ravel()
        theta = np.linspace(0, 2 * np.pi, self.resolution[0])
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
        # ==============================================================================================================

        # -----Linear interpolation-------------------------------------------------------------------------------------
        if len(self.seg_values) == 17:
            interp_data = self._interpolate_17_aha_values(self.seg_values)
        elif len(self.seg_values) == 18:
            interp_data = self._interpolate_18_aha_values(self.seg_values)
        elif len(self.seg_values) == 65:
            interp_data = self._interpolate_65_values(self.seg_values)
        else:
            exit('Wrong number of segments provided: {}'.format(len(self.seg_values)))
            return -1

        r = np.linspace(0, 1, interp_data.shape[0])
        # ==============================================================================================================

        # -----Fill segments -------------------------------------------------------------------------------------------
        r0 = np.repeat(r[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = np.repeat(theta[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data
        z = z.T

        # Color the plot
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0, r0, z, cmap=cmap, levels=self.levels)
            cf.ax.axis('off')
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)

        if len(self.seg_values) == 65:
            self._interpolate_65_to_17_values()

        # Annotate
        for i in range(6):
            # Segments 1-6
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[73:]),  # position (circumferential, norm)
                    int(self.seg_values[i]),  # value
                    fontsize=20, ha='center', va='center', color='w',  # font options
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            # Segments 7-12
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[46:73]), int(self.seg_values[i+6]),
                    fontsize=20, ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            # Segment names
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i], weight='bold',
                    color=self.COLORS[i], path_effects=[pef.Stroke(linewidth=1, foreground='k'), pef.Normal()])
        # Segments 13-16
        for i in range(4):
            ax.text(np.deg2rad(i * 90) + np.deg2rad(seg_align_13_16[i]), np.mean(r[20:46]), int(self.seg_values[i + 12]),
                    fontsize=20, ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # Segment 17
        ax.text(0, 0, int(self.seg_values[16]), fontsize=20, ha='center', va='center', color='w',
                path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
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

    def bullseye_18_smooth(self, fig, ax, cmap='jet', norm=None, units='Units', title='Smooth 18 AHA plot',
                           smooth_contour=False, echop=False):
        """
        Function to create the smooth representation of the AHA 18 segment plot
        :param fig: matplotlib.pyplot.figure
            The plot is drawn on this figure
        :param ax: matplotlib.pyplot.axes
            Axes of the figure, for 18 AHA and colorbar.
        :param cmap: ColorMap or None, optional
            Optional argument to set the desired colormap
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
            seg_names = self.ECHOP_SEGMENT_ABBRV
            seg_names_pos = [0.1, 0.06, 0.1, 0.1, 0.06, 0.1]
        else:
            rot = [0, 60, -60, 0, 60, -60]
            seg_align = 90
            seg_names = self.AHA_SEGMENT_NAMES
            seg_names_pos = np.repeat([0.06], 6)

        # -----Basic assumptions on resolution--------------------------------------------------------------------------
        self.seg_values = np.array(self.seg_values).ravel()
        theta = np.linspace(0, 2 * np.pi, self.resolution[0])
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
        elif len(self.seg_values) == 65:
            interp_data = self._interpolate_65_values(self.seg_values)
        else:
            exit('Wrong number of segments provided: {}'.format(len(self.seg_values)))
            return -1

        r = np.linspace(0, 1, interp_data.shape[0])
        # ==============================================================================================================

        # -----Fill segments 1:18---------------------------------------------------------------------------------------
        r0 = r
        r0 = np.repeat(r0[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data
        z = z.T

        # Annotate
        for i in range(6):
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.84, int(self.seg_values[i]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.55, int(self.seg_values[i + 6]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.25, int(self.seg_values[i + 12]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            # Segment names
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center',  va='center', rotation=rot[i],
                    color=self.COLORS[i], path_effects=[pef.Stroke(linewidth=1, foreground='k'), pef.Normal()])
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

        # self.seg_values = self._get_segmental_values(data)

        cmap = plt.get_cmap('seismic')
        norm = (3, 10)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1,
                               subplot_kw=dict(projection='polar'))
        if self.n_segments == 18:
            fig = self.bullseye_18_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness',
                                          units='mm', smooth_contour=False, echop=echop)
        else:
            fig = self.bullseye_17_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Wall thickness',
                                          units='mm', smooth_contour=False, echop=echop)
        fig.savefig(os.path.join(self.output_path, filename))