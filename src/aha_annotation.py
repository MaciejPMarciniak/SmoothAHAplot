import numpy as np
import matplotlib.pyplot as plt

from src import aha_segmental_values, plot_style
from src.parameters import AHA_FEATURES, PLOT_COMPONENTS


def correct_negative_zero(func):
    """Removes a minus from annotation if value is close to 0.

    Args:
        func: Annotating function
    """

    def wrapper(self, angle: float, position: float, value: float | int):
        corrected_value = 0 if np.abs(np.round(value, 1)) < 0.1 else int(value)
        return func(self, angle, position, corrected_value)

    return wrapper


class AHAAnnotation:
    """A class for annotation of the AHA plot with values of the biomarkers."""

    def __init__(
        self, segments: aha_segmental_values.AHASegmentalValues | list[float], ax: plt.Axes
    ) -> None:
        self.segments = segments
        self.ax = ax
        self.pu = plot_style.Alignment()

    @property
    def n_segments(self) -> int:
        return str(len(self.segments))

    @property
    def n_segment_angles(self) -> int:
        return len(AHA_FEATURES["walls"])

    def annotate_aha_segments(self):
        self._annotate_basal_segments()
        self._annotate_mid_segments()
        self._annotate_apical_segments()

    def _annotate_basal_segments(self):
        """Inserts the biomarker values in the basal segments."""
        for segment in range(self.n_segment_angles):
            angle = self._get_annotation_angle(segment)
            position = float(
                np.mean(
                    [
                        PLOT_COMPONENTS[self.n_segments][-2],
                        PLOT_COMPONENTS[self.n_segments][-1],
                    ]
                )
            )
            self._annotate_segment(angle, position, self.segments.segmental_values[segment])

    def _annotate_mid_segments(self):
        """Inserts the biomarker values in the mid segments."""
        for segment in range(self.n_segment_angles):
            angle = self._get_annotation_angle(segment)
            position = float(
                np.mean(
                    [
                        PLOT_COMPONENTS[self.n_segments][-3],
                        PLOT_COMPONENTS[self.n_segments][-2],
                    ]
                )
            )
            self._annotate_segment(angle, position, self.segments.segmental_values[segment + 6])

    def _annotate_apical_segments(self):
        """Inserts the biomarker values in the apical segments."""
        if self.n_segments == "17":
            n_apical_angles = 4
            for segment in range(n_apical_angles):
                angle = self._get_annotation_angle(segment, n_apical_angles)
                position = float(
                    np.mean(
                        [
                            PLOT_COMPONENTS[self.n_segments][0],
                            PLOT_COMPONENTS[self.n_segments][1],
                        ]
                    )
                )
                self._annotate_segment(
                    angle, position, self.segments.segmental_values[segment + 12]
                )

            angle = position = 0
            self._annotate_segment(angle, position, self.segments.segmental_values[-1])
        else:
            for segment in range(self.n_segment_angles):
                angle = self._get_annotation_angle(segment)
                position = PLOT_COMPONENTS["positional_parameters"]["apical_position"]
                self._annotate_segment(
                    angle, position, self.segments.segmental_values[segment + 12]
                )

    @correct_negative_zero
    def _annotate_segment(self, angle: float, position: float, value: int | float):
        self.ax.text(angle, position, value, PLOT_COMPONENTS["values_style"])

    def _get_annotation_angle(self, segment: int, angles: int | None = None):
        if angles is None:
            return np.deg2rad(self.pu.annotation_shift_functions[self.n_segment_angles](segment))

        assert angles == 4, f"Inccorrect number of {angles=} provided."
        return np.deg2rad(self.pu.annotation_shift_functions[angles](segment))
