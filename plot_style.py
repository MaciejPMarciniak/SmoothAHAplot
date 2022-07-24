import matplotlib.patheffects as pef


class PlotStyle:

    segment_name_colors = ['cyan', 'yellow', 'red', 'blue', 'magenta', 'green']

    values_style = {'fontsize': 20, 'ha': 'center', 'va': 'center', 'color': 'w',
                         'path_effects': [pef.Stroke(linewidth=3, foreground='k'), pef.Normal()]}