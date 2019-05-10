import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pef
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


class Smooth17AHAPlot:
    """
    Class for producing smooth 17 segment left ventricle plot, recommended by American Heart Association:
        http://www.pmod.com/files/download/v34/doc/pcardp/3615.htm
    Inspired with the 'bullseye plot':
        https://matplotlib.org/gallery/specialty_plots/leftventricle_bulleye.html
    Available at:
        https://github.com/MaciejPMarciniak/smooth17AHAplot

    Two helper methods are included, adjusted to plot myocardial work and strain values with proper scales.
    """

    AHA_17_SEGMENT_NAMES = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
                            'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
                            'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
                            'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
                            'Apical Anterior', 'Apical Septal', 'Apical Inferior', 'Apical Lateral', 'Apex']

    ECHOP_SEGMENT_NAMES = ['ANT', 'ANT_SEPT', 'SEPT', 'INF', 'POST', 'LAT']

    def __init__(self, data, output_path='', plot_filename='AHA_17_plot.png'):

        if data is None:
            self.data = [0] * 17
            print('No data provided. Please provide 17 segmental values for the plot: Smooth17AHAPlot.data = ...')
        else:
            assert len(data) == 17, 'Please provide 17 segmental values for the plot. len(data) = {}'.format(len(data))
            self.data = data
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
        if aha_values is None:
            aha_values = self.data

        res_x = self.resolution[0]
        res_y = self.resolution[1]

        # Extract values
        basal = aha_values[:6]
        mid = aha_values[6:12]
        apical = aha_values[12:16]
        apex = aha_values[16]

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

        # Align to the proper position of the segments
        basal_interp = np.roll(basal_interp, int(res_x / 4))
        mid_interp = np.roll(mid_interp, int(res_x / 4))
        apical_interp = np.roll(apical_interp, int(res_x / 3)-32)

        # Helper arrays for better basal segments visualization
        _tmp_basal = basal_interp * 4
        _tmp_mid = mid_interp
        _basal_low = (_tmp_basal + _tmp_mid) / 5

        # Put it all together
        full_map = np.array([basal_interp, _basal_low, mid_interp, apical_interp, apex_interp])
        full_map = np.flip(full_map, 0)
        y_0 = [0, 0.33, 0.55, 0.85, 1]
        f = interp1d(y_0, full_map, axis=0)
        full_map_interp = f(np.linspace(0, 1, res_y))

        return full_map_interp

    def bullseye_smooth(self, fig, ax, cmap='jet', norm=None, units='Units', title='Smooth 17 AHA plot',
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
            seg_names = self.ECHOP_SEGMENT_NAMES
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
        # Create the bound for the segment 17
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
        interp_data = self._interpolate_17_aha_values(self.data)

        r = np.linspace(0, 1, interp_data.shape[0])
        d_theta = 1 / interp_data.shape[1]
        d_r = 1 / interp_data.shape[0]
        # ==============================================================================================================

        # -----Fill segments 1:6----------------------------------------------------------------------------------------
        r0 = r[73:]
        r0 = np.repeat(r0[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data[73:, :]
        z = z.T

        # Annotate
        for i in range(6):
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[73:]), int(self.data[i]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), r[-1] + seg_names_pos[i], seg_names[i],
                    fontsize=20, ha='center', va='center', rotation=rot[i])
        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0[:-1, :-1] + d_theta / 2.,
                             r0[:-1, :-1] + d_r / 2., z[:-1, :-1], cmap=cmap, levels=self.levels)
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)
        # ==============================================================================================================

        # -----Fill segments 7-12---------------------------------------------------------------------------------------
        r0 = r[46:75]
        r0 = np.repeat(r0[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data[46:75, :]
        z = z.T

        # Annotate
        for i in range(6):
            ax.text(np.deg2rad(i * 60) + np.deg2rad(seg_align_12), np.mean(r[46:75]), int(self.data[i + 6]), fontsize=20,
                    ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0[:-1, :-1] + d_theta / 2.,
                             r0[:-1, :-1] + d_r / 2., z[:-1, :-1], cmap=cmap, levels=self.levels)
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)
        # ==============================================================================================================

        # -----Fill segments 13-16--------------------------------------------------------------------------------------
        r0 = r[20:48]
        r0 = np.repeat(r0[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data[20:48, :]
        z = z.T

        # Annotate
        for i in range(4):
            ax.text(np.deg2rad(i * 90) + np.deg2rad(seg_align_13_16[i]), np.mean(r[20:46]), int(self.data[i + 12]),
                    fontsize=20, ha='center', va='center', color='w',
                    path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0[:, :-1] + d_theta / 2.,
                             r0[:, :-1] + d_r / 2., z[:, :-1], cmap=cmap, levels=self.levels)
        else:
            ax.pcolormesh(theta0, r0, z, cmap=cmap, norm=norm)
        # ==============================================================================================================

        # -----Fill segment 17------------------------------------------------------------------------------------------
        r0 = r[:22]
        r0 = np.repeat(r0[:, np.newaxis], self.resolution[0], axis=1).T
        theta0 = theta
        theta0 = np.repeat(theta0[:, np.newaxis], r0.shape[1], axis=1)
        z = interp_data[0:22, :]
        z = z.T

        # Annotate
        ax.text(0, 0, int(self.data[16]), fontsize=20, ha='center', va='center', color='w',
                path_effects=[pef.Stroke(linewidth=3, foreground='k'), pef.Normal()])
        # Colour
        if smooth_contour and (self.levels is not None):
            cf = ax.contourf(theta0[:-1, :-1] + d_theta / 2.,
                             r0[:-1, :-1] + d_r / 2., z[:-1, :-1], cmap=cmap, levels=self.levels)
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
            assert len(data) == 17, 'Please provide 17 segmental values for the plot. len(data) = {}'.format(len(data))
            self.data = data

        cmap = 'rainbow'
        norm = (1000, 3000)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1,
                               subplot_kw=dict(projection='polar'))
        fig = self.bullseye_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Myocardial work index', units='mmHg%',
                                   smooth_contour=False, echop=echop)
        fig.savefig(os.path.join(self.output_path, self.plot_filename))

    def plot_strain(self, filename='', data=None, echop=False):

        if filename != '':
            self.plot_filename = filename
        if data is not None:
            assert len(data) == 17, 'Please provide 17 segmental values for the plot. len(data) = {}'.format(len(data))
            self.data = data

        self.levels = MaxNLocator(nbins=12).tick_values(-30, 30)
        cmap = plt.get_cmap('seismic_r')
        norm = BoundaryNorm(self.levels, ncolors=cmap.N, clip=True)
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1, subplot_kw=dict(projection='polar'))
        fig = self.bullseye_smooth(fig=fig, ax=ax, cmap=cmap, norm=norm, title='Longitudinal strain', units='%',
                                   smooth_contour=True, echop=echop)
        fig.savefig(os.path.join(self.output_path, self.plot_filename))


if __name__ == '__main__':
    exp_strain_data = [-13, -14, -16, -19, -19, -18, -19, -23, -17, -21, -20, -20, -23, -24, -28, -25, -26]
    exp_mw_data = [1926, 1525, 1673, 2048, 2325, 2200, 2197, 2014, 1982, 2199, 2431, 2409, 2554, 2961, 2658, 2729, 2833]
    df_hyp = pd.read_excel('/home/mat/Python/data/parsing_xml/output/population_17_AHA.xlsx', index_col=0)
    aha = Smooth17AHAPlot(exp_strain_data, output_path='/home/mat/Python/data/parsing_xml/output',
                          plot_filename='17_AHA_strain.png')
    aha.plot_strain('ctrl_strain.png', data=df_hyp.loc['mean_strain_avc_0'].values, echop=True)
    aha.plot_strain('htn_strain.png', data=df_hyp.loc['mean_strain_avc_1'].values, echop=True)
    aha.plot_strain('bsh_strain.png', data=df_hyp.loc['mean_strain_avc_2'].values, echop=True)
    aha.plot_myocardial_work('ctrl_MW.png', data=df_hyp.loc['mean_MW_0'].values, echop=True)
    aha.plot_myocardial_work('htn_MW.png', data=df_hyp.loc['mean_MW_1'].values, echop=True)
    aha.plot_myocardial_work('bsh_MW.png', data=df_hyp.loc['mean_MW_2'].values, echop=True)
    # aha.plot_strain()
    # aha.plot_myocardial_work('17_AHA_MW.png', data=exp_mw_data)
    # aha.plot_strain('17_AHA_Echo_strain.png', data=exp_strain_data, echop=True)
    # aha.plot_myocardial_work('17_AHA_Echo_MW.png', data=exp_mw_data, echop=True)
