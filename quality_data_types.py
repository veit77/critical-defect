""" provides data types for analysing defect structures in HTS tapes
"""
from typing import List, NamedTuple, Optional, Protocol
from enum import Enum


class QualityParameterInfo(Protocol):
    """ Protocol for defect information
    """
    number: int
    start_position: float
    end_position: float
    center_position: float
    width: float
    value: float
    description: str


class PeakInfo:
    """ Class holding information about individual peaks.
        Conforms to QualityParameterInfo protocol
    """
    @property
    def width(self):
        return self.end_position - self.start_position

    @property
    def description(self):
        return (f"Peak at {self.center_position:.2f}m, " +
                f"width: {self.width*1000:.1f}mm, value: {self.value:.0f}A")

    def __init__(self,
                 number: int = 1,
                 start_position: float = 0.0,
                 end_position: float = 0.0,
                 center_position: float = 0.0,
                 value: float = 0.0) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.center_position = center_position
        self.value = value


class AveragesInfo:
    """ Class holding information about piecewise averages.
        Conforms to QualityParameterInfo protocol
    """
    @property
    def center_position(self):
        return (self.start_position + self.end_position) / 2.0

    @property
    def width(self):
        return self.end_position - self.start_position

    @property
    def description(self):
        return (f"Average between {self.start_position:.2f}m and " +
                f"{self.end_position:.2f}m is {self.value:.0f}A")

    def __init__(self,
                 number: int = 0,
                 start_position: float = 0.0,
                 end_position: float = 0.0,
                 value: float = 0.0) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.value = value


class ScatterInfo:
    """ Class holding information about piecewise scatter characteristics.
        Conforms to QualityParameterInfo protocol
    """
    @property
    def center_position(self):
        return (self.start_position + self.end_position) / 2.0

    @property
    def width(self):
        return self.end_position - self.start_position

    @property
    def description(self):
        return (f"Scatter between {self.start_position:.2f}m and " +
                f"{self.end_position:.2f}m is {self.value:.0f}A")

    def __init__(self, number: int, start_position: float, end_position: float,
                 value: float) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.value = value


class TapeSpecs(NamedTuple):
    """ Tuple holding information about tape specifications
    """
    width: float
    min_average: float
    min_value: float
    average_length: float
    min_tape_length: float
    description: str


class TapeProduct(Enum):
    """ Enum summarizing different tape specifications
    """
    SUPERLINK_PHASE = TapeSpecs(width=3.0,
                                min_average=135.0,
                                min_value=70.0,
                                average_length=20.0,
                                min_tape_length=190.0,
                                description="SuperLink Phase")
    SUPERLINK_NEUTRAL = TapeSpecs(width=6.0,
                                  min_average=200.0,
                                  min_value=100.0,
                                  average_length=20.0,
                                  min_tape_length=190.0,
                                  description="SuperLink Neutral")
    STANDARD = TapeSpecs(width=12.0,
                         min_average=700.0,
                         min_value=500.0,
                         average_length=20.0,
                         min_tape_length=25.0,
                         description="Standard Tape")


class FailType(Enum):
    """ Enum of different failure types.

    Args:
        Enum (str): failure tape as string
    """
    AVERAGE = 'Average Failed'
    SCATTER = 'Scatter Failed'
    MINIMUM = 'Minimum Failed'
    DROP_OUT = 'Drop Out Failed'


class TapeSection(NamedTuple):
    """ Holds information of tape sections.
    """
    @property
    def length(self):
        return self.end_position - self.start_position

    start_position: float
    end_position: float


class QualityReport(NamedTuple):
    """ Class containing all information for a quality report for a tape
        regarding a specific quality parameter.
    """
    tape_id: str
    passed: bool
    type: Optional[FailType] = None
    fail_information: Optional[List[QualityParameterInfo]] = None
