from ahasmoothplot import SmoothAHAPlot
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

aha = SmoothAHAPlot(strain_dict, output_path='./images', n_segments=n_seg)

aha.plot_strain('17_AHA_strain.png', data=strain_dict)
aha.plot_myocardial_work('17_AHA_MW.png', data=mw_dict)
aha.plot_strain('17_AHA_Echo_strain.png', data=strain_dict, echop=True)
aha.plot_myocardial_work('17_AHA_Echo_MW.png', data=mw_dict, echop=True)