from ahasmoothplot import SmoothAHAPlot
import pandas as pd


exp_strain_data = [-13, -14, -16, -19, -19, -18, -19, -23, -19, -21, -20, -20, -23, -25, -28, -25, -26, -22]
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

# aha = SmoothAHAPlot(exp_strain_data, output_path='/home/mat/Python/data/parsing_xml/22 random/output',
#                     plot_filename='17_AHA_strain.png', n_segments=n_seg)
#
# df_hyp = pd.read_excel('/home/mat/Python/data/parsing_xml/22 random/output/population_18_AHA.xlsx', index_col=0)
#
# if aha.n_segments == 17:
#     df_hyp = df_hyp.reindex(aha.AHA_17_SEGMENT_NAMES, axis=1)
# else:
#     df_hyp = df_hyp.reindex(segments_18, axis=1)
#     df_hyp.columns = aha.AHA_18_SEGMENT_NAMES
#
# aha.plot_strain('htn_strain_1_aha.png', data=df_hyp.loc['mean_strain_avc_1'], echop=echop)
# aha.plot_strain('htn_strain_2_aha.png', data=df_hyp.loc['mean_strain_avc_2'], echop=echop)
# aha.plot_myocardial_work('htn_MW_1_aha.png', data=df_hyp.loc['mean_MW_1'], echop=echop)
# aha.plot_myocardial_work('htn_MW_2_aha.png', data=df_hyp.loc['mean_MW_2'], echop=echop)

aha = SmoothAHAPlot(strain_dict, output_path='./images', n_segments=n_seg)

aha.plot_strain('18_AHA_strain.png', data=strain_dict)
aha.plot_myocardial_work('18_AHA_MW.png', data=mw_dict)
aha.plot_strain('18_AHA_Echo_strain.png', data=strain_dict, echop=True)
aha.plot_myocardial_work('18_AHA_Echo_MW.png', data=mw_dict, echop=True)