import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d

from aha import aha_segmental_values
from parameters.parameters import AHA_FEATURES, PLOT_COMPONENTS

# TODO: Remove handling lists in segmental_values


class AHAInterpolation:
    """Class to interpolate provided values for smoothed plots."""

    def __init__(self, segments: aha_segmental_values.AHASegmentalValues) -> None:
        self.segments = segments

    @property
    def segmental_values(self) -> list[float | int]:
        return list(self.segments.segmental_values)

    @property
    def n_segments(self) -> int:
        return len(self.segments)

    def interpolate_aha_values(self) -> NDArray:
        """Interpolates values along vertical and horizontal axes of the plot.

        Returns:
            Values interpolated with provided resolution.
        """
        # Set up the circular interpolation matrices
        basal, mid, apex_mid, apex = self._interpolate_values_along_circle()
        along_x = np.array([basal, self._basal_mid(basal, mid), mid, apex_mid, apex])

        # Adjust for correct visualisation
        along_x = np.roll(along_x, int(PLOT_COMPONENTS["resolution"][0] / 4), axis=1)
        along_x = np.flip(along_x, 0)

        # Interpolate along the radius
        interpolator = interp1d(AHA_FEATURES[str(self.n_segments)]["levels"], along_x, axis=0)
        along_x_y = interpolator(np.linspace(0, 1, PLOT_COMPONENTS["resolution"][1]))

        return along_x_y

    def _interpolate_values_along_circle(self) -> tuple[NDArray, ...]:
        """
        Interpolate the initial values, to achieve smooth transition among segments.

        Returns:
            Interpolated values around the radial direction.
        """
        basal = self._interpolate_directions(self.segmental_values[:6])
        mid = self._interpolate_directions(self.segmental_values[6:12])
        if self.n_segments == 17:
            apex_mid = self._interpolate_directions(self.segmental_values[12:16])
            apex = np.repeat(self.segmental_values[16], PLOT_COMPONENTS["resolution"][0])
        else:
            apex_mid = self._interpolate_directions(self.segmental_values[12:])
            apex = np.repeat(
                np.sum(self.segmental_values[12:]) / 6, PLOT_COMPONENTS["resolution"][0]
            )
        return basal, mid, apex_mid, apex

    @staticmethod
    def _basal_mid(basal: NDArray, mid: NDArray) -> NDArray:
        """Helper array for better basal segments visualization

        Args:
            basal: Values at the basal segment
            mid: Values at the mid segment

        Returns:
            Additional array used for interpolation
        """
        return (basal * 3 + mid) / 4

    def _interpolate_directions(self, regional_values: list[float | int]) -> NDArray:
        """Interpolates provided values with set resolution.

        Args:
            regional_values: Values between which the interpolation occurs.

        Returns:
            The result of interpolation, with length equal to the set resolution.
        """
        res = PLOT_COMPONENTS["resolution"][0]
        n_segments = len(regional_values)
        interpolated_array = np.zeros(res)

        for i in range(n_segments):
            interpolated_array[
                int(res / n_segments) * i : int(res / n_segments * i + res / n_segments)
            ] = np.linspace(
                regional_values[i], regional_values[(i + 1) % n_segments], int(res / n_segments)
            )

        return interpolated_array
