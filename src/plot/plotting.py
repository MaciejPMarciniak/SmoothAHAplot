from typing import Type

import pydantic
from loguru import logger
from matplotlib import colorbar, pyplot

from aha import aha_interpolation, aha_segmental_values
from parameters.parameters import BIOMARKER_FEATURES, PLOT_COMPONENTS
from plot import biomarker


class BiomarkerError(NotImplementedError):
    pass


class AHAPlotting(pydantic.BaseModel):
    """Class for managing the plot components, including coloring,
    grid, ticks, labels, and title."""

    ax: pyplot.Axes
    fig: pyplot.Figure
    biomarker_name: str

    def __init__(self, **data: dict) -> None:
        super().__init__(**data)
        self._biomarker_handler = self.get_biomarker()

    @pydantic.field_validator("biomarker_name")
    @classmethod
    def biomarker_name_validator(cls) -> None:
        """Asserts the biomarker coloring object exists

        Args:
            biomarker_name: The marker of the cardiac anatomy/function

        Raises:
            BiomarkerError: If the biomarker handling class does not exist
        """
        if cls.biomarker_name not in BIOMARKER_FEATURES.keys:
            raise BiomarkerError(
                logger.error(
                    f"Plot settings for the biomarker {cls.biomarker_name} do not exist. "
                    f"Available biomarkers: {BIOMARKER_FEATURES.keys}"
                )
            )

    @classmethod
    def get_biomarker(cls) -> Type[biomarker.Biomarker]:
        return [
            subclass
            for subclass in biomarker.Biomarker.__subclasses__()
            if subclass.biomarker_name == cls.biomarker_name
        ][0]

    def color_plot(
        self,
        segments: aha_segmental_values.AHASegmentalValues,
    ) -> pyplot.Axes:
        self._clear_bullseye_plot()
        interpolator = aha_interpolation.AHAInterpolation(segments=segments)
        interpolated_segment_values = interpolator.interpolate_aha_values()
        self.ax = self._biomarker_handler.color_plot(self.ax, interpolated_segment_values)
        return self.ax

    def _clear_bullseye_plot(self) -> None:
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        self.ax.set_ylim(
            [PLOT_COMPONENTS["bound_range"]["inner"], PLOT_COMPONENTS["bound_range"]["outer"]]
        )
        self.ax.grid(None)

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
