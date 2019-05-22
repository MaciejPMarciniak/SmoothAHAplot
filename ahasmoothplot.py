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

    # If a pandas dataframe is provided, it should have the following names:
    AHA_17_SEGMENT_NAMES = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
                            'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
                            'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
                            'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
                            'Apical Anterior', 'Apical Septal', 'Apical Inferior', 'Apical Lateral', 'Apex']
    # or
    ECHOP_18_SEGMENTS = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Septal',
                         'Basal Inferior', 'Basal Posterior', 'Basal Lateral',
                         'Mid Anterior', 'Mid Anteroseptal', 'Mid Septal',
                         'Mid Inferior', 'Mid Posterior', 'Mid Lateral',
                         'Apical Anterior', 'Apical Anteroseptal', 'Apical Septal',
                         'Apical Inferior', 'Apical Posterior', 'Apical Lateral']

    # The actual names of the segments:
    AHA_SEGMENT_NAMES = ['Anterior', 'Anteroseptal', 'Inferoseptal',
                         'Inferior', 'Inferolateral', 'Anterolateral']
    # EchoPAC version of the names:
    ECHOP_SEGMENT_ABBRV = ['ANT', 'ANT_SEPT', 'SEPT', 'INF', 'POST', 'LAT']

    def __init__(self, data, output_path='', plot_filename='AHA_plot.png', n_segments=17):

        if data is None:
            self.data = [0] * n_segments
            print('No data provided. Please provide segmental values for the plot: SmoothAHAPlot.data = ...')
        else:
            assert len(data) == n_segments, 'Please provide the proper number of segmental values for the plot. ' \
                                            'len(data) = {}, n_segments: {}'.format(len(data), n_segments)
            self.data = data
        self.n_segments = n_segments
        self.output_path = output_path
        self.plot_filename = plot_filename
        self.levels = None
        self.fig = None
        self.resolution = (768, 100)

    def _interpolate_17_aha_values(self, aha_values=None):
        """
        Funtion to interpolate the initial 17 values, to achieve smooth transition among segments.
        :param aha_values: list, tuple
            The 17 values
        :return:
        """
        assert len(self.data) == 17, 'Please provide the proper number of segmental values for the 17 AHA plot. ' \
                                     'len(data) = {}'.format(len(self.data))
        if aha_values is None:
            aha_values = self.data

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
        assert len(self.data) == 18, 'Please provide the proper number of segmental values for the 18 AHA plot. ' \
                                     'len(data) = {}'.format(len(self.data))
        if aha_values is None:
            aha_values = self.data

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
            norm = mpl.colors.Normalize(vmin=self.data.min(), vmax=self.data.max())
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
        self.data = np.array(self.data).ravel()
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
        if self.n_segments == 17:
            interp_data = self._interpolate_17_aha_values(self.data)
        else:
            interp_data = self._interpolate_18_aha_values(self.data)

        r = np.linspace(0, 1, interp_data.shape[0])
        # ==============================================================================================================

        # -----Fill segments 1:12---------------------------------------------------------------------------------------
        r0 = np.repeat(r[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = np.repeat(theta[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data
        z = z.T

        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0, r0, z, cmap=cmap, levels=self.levels)
            cf.ax.axis('off')
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)

        # Annotate
        for i in range(6):
            # Segments 1-6
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[73:]), int(self.data[i]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            # Segments 7-12
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[46:73]), int(self.data[i+6]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            # Sides
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i])
        # Segments 13-16
        for i in range(4):
            ax.text(np.deg2rad(i * 90) + np.deg2rad(seg_align_13_16[i]), np.mean(r[20:46]), int(self.data[i + 12]),
                    fontsize=20, ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # Segment 17
        ax.text(0, 0, int(self.data[16]), fontsize=20, ha='center', va='center', color='w',
                path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # ==============================================================================================================

        # -----Add plot featres-----------------------------------------------------------------------------------------
        # Create the axis for the colorbars
        bar = fig.add_axes([0.12, 0.15, 0.2, 0.05])
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
            norm = mpl.colors.Normalize(vmin=self.data.min(), vmax=self.data.max())
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
        self.data = np.array(self.data).ravel()
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
        if self.n_segments == 17:
            interp_data = self._interpolate_17_aha_values(self.data)
        else:
            interp_data = self._interpolate_18_aha_values(self.data)

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
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.84, int(self.data[i]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.55, int(self.data[i + 6]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), 0.25, int(self.data[i + 12]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i])

        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0, r0, z, cmap=cmap, levels=self.levels)
            cf.ax.axis('off')
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)
        # ==============================================================================================================

        # -----Add plot featres-----------------------------------------------------------------------------------------
        # Create the axis for the colorbars
        bar = fig.add_axes([0.12, 0.15, 0.2, 0.05])
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

    def plot_myocardial_work(self, filename='', data=None, echop=False):

        if filename != '':
            self.plot_filename = filename
        if data is not None:
            assert len(data) == self.n_segments, 'Please provide correct number of segmental values for the plot. ' \
                                                 'len(data) = {}, n_segments =  {}'.format(len(data), self.n_segments)
            self.data = data

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
        fig.savefig(os.path.join(self.output_path, self.plot_filename))

    def plot_strain(self, filename='', data=None, echop=False):

        if filename != '':
            self.plot_filename = filename
        if data is not None:
            assert len(data) == self.n_segments, 'Please provide correct number of segmental values for the plot. ' \
                                                 'len(data) = {}, n_segments =  {}'.format(len(data), self.n_segments)
            self.data = data

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
        fig.savefig(os.path.join(self.output_path, self.plot_filename))

    def plot_all(self, df_path='', echop=True):

        df_hyp = pd.read_excel(df_path, index_col=0)

        if self.n_segments == 17:
            df_hyp = df_hyp.reindex(self.AHA_17_SEGMENT_NAMES, axis=1)
        else:
            df_hyp = df_hyp.reindex(self.ECHOP_18_SEGMENTS, axis=1)

        aha.plot_strain('htn_strain_0_aha_EPC.png', data=df_hyp.loc['mean_strain_avc_0'].values, echop=echop)
        aha.plot_strain('htn_strain_1_aha_EPC.png', data=df_hyp.loc['mean_strain_avc_1'].values, echop=echop)
        aha.plot_myocardial_work('htn_MW_0_aha_EPC.png', data=df_hyp.loc['mean_MW_0'].values, echop=echop)
        aha.plot_myocardial_work('htn_MW_1_aha_EPC.png', data=df_hyp.loc['mean_MW_1'].values, echop=echop)
        aha.plot_strain('strain_all_EPC.png', data=df_hyp.loc['mean_strain_avc'].values, echop=echop)
        aha.plot_myocardial_work('MW_all_EPC.png', data=df_hyp.loc['mean_MW'].values, echop=echop)


if __name__ == '__main__':
    exp_strain_data = [-13, -14, -16, -19, -19, -18, -19, -23, -1, -21, -20, -20, -23, 1, -28, -25, -26, 27]
    exp_mw_data = [1926, 1525, 1673, 2048, 2325, 2200, 2197, 2014, 1982, 2199, 2431, 2409, 2554, 2961, 2658, 2729, 2833]

    n_seg = 17
    exp_strain_data = exp_strain_data[:n_seg]
    aha = SmoothAHAPlot(exp_strain_data, output_path='/home/mat/Python/data/parsing_xml/mr_output',
                        plot_filename='17_AHA_strain.png', n_segments=n_seg)
    aha.plot_all('/home/mat/Python/data/parsing_xml/mr_output/population_17_AHA.xlsx', echop=True)

    # aha.plot_strain()
    # aha.plot_myocardial_work('17_AHA_MW.png', data=exp_mw_data)
    # aha.plot_strain('17_AHA_Echo_strain.png', data=exp_strain_data, echop=True)
    # aha.plot_myocardial_work('17_AHA_Echo_MW.png', data=exp_mw_data, echop=True)
