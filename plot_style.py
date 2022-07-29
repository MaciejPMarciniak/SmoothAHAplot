import matplotlib.patheffects as pef
import numpy as np


class PlotStyle:

    _aha_bounds = {17: np.linspace(0.2, 1, 4), 18: np.linspace(0.38, 1, 3)}

    _values_style = {'fontsize': 20, 'ha': 'center', 'va': 'center', 'color': 'w',
                     'path_effects': [pef.Stroke(linewidth=3, foreground='k'), pef.Normal()]}

    _segment_name_style = {'fontsize': 20,
                           'ha': 'center',
                           'va': 'center',
                           'weight': 'bold',
                           'color': 'k'}

    _segment_border_style = {'linewidth': 2, 'linestyle': '-', 'color': 'k', }

    _positional_parameters = {'segment_name_orientations': (0, 60, -60, 0, 60, -60),
                              'segment_names_direction': 90,
                              'segment_names_position': 0.06}

    @property
    def values_style(self):
        return self._values_style

    @property
    def positional_parameters(self):
        return self._positional_parameters

    @property
    def segment_name_style(self):
        return self._segment_name_style

    @property
    def aha_bounds(self):
        return self._aha_bounds

    @property
    def segment_border_style(self):
        return self._segment_border_style


class PlotUtil:

    _segment_alignment_angle = 90

    @property
    def seg_align(self):
        return self._segment_alignment_angle

    @staticmethod
    def _shift_by_60(x: int) -> int:
        return x * 60

    @staticmethod
    def _shift_by_60_with_correction(x: int):
        return x * 60 + 90

    @staticmethod
    def _shift_by_90(x: int) -> int:
        return x * 90

    @staticmethod
    def _shift_by_90_with_correction(x: int) -> int:
        return x * 90 - 45

    @property
    def border_shift_functions(self):
        return {4: self._shift_by_90_with_correction, 6: self._shift_by_60}

    @property
    def annotation_shift_functions(self):
        return {4: self._shift_by_90, 6: self._shift_by_60_with_correction}