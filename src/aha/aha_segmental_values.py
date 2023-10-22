import pydantic
from loguru import logger

from src.parameters.parameters import AHA_FEATURES


class SegmentsError(AttributeError):
    """An error related to AHA segments"""


class SegmentsNameError(SegmentsError):
    """An error related to segment names"""


class SegmentSizeError(SegmentsError):
    """An error related to number of segments"""


class AHASegmentalValues(pydantic.BaseModel):
    """Class for holding a set of AHA values.

    Attributes:
        segments: Ordered AHA segments with values.
    """

    segments: dict

    def __init__(self, **data: dict) -> None:
        super().__init__(**data)
        self._segmental_values: list[int | float] = []
        self._parse_segmental_values()

    @pydantic.field_validator("segments")
    @classmethod
    def segment_validator(cls) -> None:
        """Validates provided segments

        Args:
            segments: Segments to be validated

        Raises:
            SegmentsError: If there are inconsistencies with segments defined in JSON
            SegmentSizeError: If the number of segments is different than 17 or 18
            SegmentsNameError: If the names of the segments are not the same as in JSON
        """
        try:
            correct_segment_names = AHA_FEATURES[str(len(cls.segments))]["names"]
        except SegmentSizeError as err:
            raise SegmentsError(
                logger.error(
                    f"Incorrect number of segments provided: {len(cls.segments)=}. "
                    "Provide either 17 or 18 segment values"
                )
            ) from err

        if len(correct_segment_names) != len(cls.segments):
            raise SegmentSizeError(
                f"Inconsistent number of segment values provided: {len(correct_segment_names)=} is"
                f" different from {len(cls)=}. Provide correct number of segments."
            )

        for correct_name, field_name in zip(correct_segment_names, cls.segments):
            if field_name != correct_name:
                raise SegmentsNameError(f"Incorrect segment name provided: {field_name}")

    @property
    def segmental_values(self) -> list[float]:
        return self._segmental_values

    def _parse_segmental_values(self) -> None:
        for segment_name in AHA_FEATURES[str(len(self.segments))]["names"]:
            self._segmental_values.append(self.segments[segment_name])
