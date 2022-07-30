from smoothahaplot import AHAPlotting
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import pandas as pd


exp_strain_data = [-13, -14, -16, -19, -19, -18, -19, -23, -19, -21, -20, -20, -24, -27, -28, -25, -26, -22]
exp_mw_data = [1926, 1525, 1673, 2048, 2325, 2200, 2197, 2014, 1982, 2199, 2431, 2409, 2554, 2961, 2658, 2329, 2533, 2441]
n_seg = 18
echop = False
segments_18 = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
               'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
               'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
               'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
               'Apical Anterior', 'Apical Anteroseptal', 'Apical Inferoseptal',
               'Apical Inferior', 'Apical Inferolateral', 'Apical Anterolateral']

strain_dict = {k: v for (k, v) in zip(segments_18, exp_strain_data)}
mw_dict = {k: v for (k, v) in zip(segments_18, exp_mw_data)}

aha = AHAPlotting(values=exp_strain_data, plot_output_path='./images')
levels = MaxNLocator(nbins=12).tick_values(-30, 30)
cmap = plt.get_cmap('seismic_r')
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
aha.bullseye_17_smooth(cmap=cmap, norm=norm, units='%', smooth_contour=True)
plt.show()
