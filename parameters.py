from typing import Tuple
import numpy as np

# pandas Series/dictionary must have following index/keys:
AHA_SEGMENT_NAMES = {
    17: ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
         'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
         'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
         'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
         'Apical Anterior', 'Apical Septal', 'Apical Inferior', 'Apical Lateral',
         'Apex'],

    18: ['Basal Anterior', 'Basal Anteroseptal', 'Basal Inferoseptal',
         'Basal Inferior', 'Basal Inferolateral', 'Basal Anterolateral',
         'Mid Anterior', 'Mid Anteroseptal', 'Mid Inferoseptal',
         'Mid Inferior', 'Mid Inferolateral', 'Mid Anterolateral',
         'Apical Anterior', 'Apical Anteroseptal', 'Apical Inferoseptal',
         'Apical Inferior', 'Apical Inferolateral', 'Apical Anterolateral'],

    'walls': ['Anterior', 'Anteroseptal', 'Inferoseptal', 'Inferior', 'Inferolateral', 'Anterolateral']}


class InterpolationParameters:

    def __init__(self):
        self._resolution = (768, 100)
        self._plot_levels = ()
        self._segment_group_borders = ()

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, res: Tuple[int]):
        assert res[0] > 0, 'Resolution x must be greater than 0'
        assert res[1] > 0, 'Resolution y must be greater than 0'
        assert len(res) == 2, 'Exactly 2 resolution parameters are allowed'
        self._resolution = res

    @property
    def plot_levels(self):
        return self._plot_levels

    @plot_levels.setter
    def plot_levels(self, levels: Tuple[float]):
        for level in levels:
            assert 0 <= level <= 1, 'Level value must be between 0 and 1'
        self._plot_levels = levels

    @property
    def radial_position(self):
        return np.linspace(0, 1, self.resolution[1])


class AHA17Parameters(InterpolationParameters):

    def __init__(self):
        super().__init__()
        self.plot_levels = (0, 0.33, 0.55, 0.85, 1)


class AHA18Parameters(InterpolationParameters):

    def __init__(self):
        super().__init__()
        self.plot_levels = (0, 0.28, 0.5, 0.8, 1)
