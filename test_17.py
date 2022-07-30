from smoothahaplot import AHAPlotting
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import pandas as pd


exp_strain_data = [-13, -14, -16, -20, -19, -18, -19, -23, -19, -21, -20, -20, -23, -22, -28, -25, -26]
exp_mw_data = [1926, 1525, 1673, 2048, 2325, 2200, 2197, 2014, 1982, 2199, 2431, 2409, 2554, 2961, 2328, 2329, 2288]
n_seg = 17
echop = False
segments_17 = ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
               'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
               'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
               'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
               'Apical Anterior', 'Apical Septal', 'Apical Inferior', 'Apical Lateral', 'Apex']

strain_dict = {k: v for (k, v) in zip(segments_17, exp_strain_data)}
mw_dict = {k: v for (k, v) in zip(segments_17, exp_mw_data)}

aha = AHAPlotting(values=exp_mw_data, plot_output_path='./images')
cmap = plt.get_cmap('rainbow')
norm = (1000, 3000)
aha.bullseye_17_smooth(cmap=cmap, norm=norm, title='Myocardial work index', units='mmHg%', smooth_contour=False)

# levels = MaxNLocator(nbins=12).tick_values(-30, 30)
# cmap = plt.get_cmap('seismic_r')
# norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
# aha.bullseye_17_smooth(cmap=cmap, norm=norm, units='%', smooth_contour=True)
plt.show()