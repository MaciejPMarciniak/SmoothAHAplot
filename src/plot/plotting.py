from typing import Type

import pydantic
from loguru import logger
from matplotlib import colorbar
from matplotlib import pyplot as plt

from aha import aha_interpolation, aha_segmental_values
from parameters.parameters import BIOMARKER_FEATURES, PLOT_COMPONENTS
from plot import biomarkers


class BiomarkerError(NotImplementedError):
    pass


class AHAPlotting(pydantic.BaseModel):
    """Class for managing the plot components, including coloring,
    grid, ticks, labels, and title."""

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    ax: plt.Axes
    fig: plt.Figure
    biomarker_name: str

    def __init__(self, **data: dict) -> None:
        super().__init__(**data)
        self._biomarker_handler = self.get_biomarker()

    @pydantic.field_validator("biomarker_name")
    @classmethod
    def biomarker_name_validator(cls, value: dict) -> dict:
        """Asserts the biomarker coloring object exists

        Args:
            biomarker_name: The marker of the cardiac anatomy/function

        Raises:
            BiomarkerError: If the biomarker handling class does not exist
        """
        if value not in BIOMARKER_FEATURES.keys():
            logger.error(
                f"Plot settings for the biomarker {value} do not exist. "
                f"Available biomarkers: {BIOMARKER_FEATURES.keys()}"
            )
            raise BiomarkerError()
        return value

    def get_biomarker(self) -> Type[biomarkers.Biomarker]:
        marker = [
            subclass
            for subclass in biomarkers.Biomarker.__subclasses__()
            if subclass.__name__ == self.biomarker_name
        ]
        if marker:
            logger.debug(f"Building '{marker[0].__name__}' handler")
            return marker[0]()
        raise BiomarkerError(f"No biomarker {self.biomarker_name} found")

    def create_plot(
        self,
        segments: aha_segmental_values.AHASegmentalValues,
    ) -> plt.Axes:
        self._clear_bullseye_plot()
        self._set_title()
        self._plot_interpolated_segmental_values(segments)
        return self.ax

    def _clear_bullseye_plot(self) -> None:
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        self.ax.set_ylim(
            [PLOT_COMPONENTS["bound_range"]["inner"], PLOT_COMPONENTS["bound_range"]["outer"]]
        )
        self.ax.grid(None)

    def _set_title(self) -> None:
        self.ax.set_title(
            BIOMARKER_FEATURES[self._biomarker_handler.__class__.__name__]["title"],
            fontsize=PLOT_COMPONENTS["title_style"]["fontsize"],
            pad=PLOT_COMPONENTS["title_style"]["pad"],
        )

    def _plot_interpolated_segmental_values(
        self, segments: aha_segmental_values.AHASegmentalValues
    ) -> None:
        interpolator = aha_interpolation.AHAInterpolation(segments=segments)
        interpolated_segment_values = interpolator.interpolate_aha_values()
        self.ax = self._biomarker_handler.color_plot(
            ax=self.ax,
            interpolated_segment_values=interpolated_segment_values,
        )

    def add_color_bar(self) -> None:
        """Adds the color bar with scale of the plot."""
        bar = self.fig.add_axes(PLOT_COMPONENTS["colorbar"]["axes"])
        cb1 = colorbar.ColorbarBase(
            bar,
            cmap=self._biomarker_handler.cmap,
            norm=self._biomarker_handler.norm,
            orientation=PLOT_COMPONENTS["colorbar"]["orientation"],
        )
        cb1.set_label(
            self._biomarker_handler.units,
            size=PLOT_COMPONENTS["colorbar"]["label_size"],
        )
        cb1.ax.tick_params(
            labelsize=PLOT_COMPONENTS["colorbar"]["tick_size"],
            which=PLOT_COMPONENTS["colorbar"]["tick_marks"],
        )
