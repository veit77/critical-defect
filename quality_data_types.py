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
    width: float
    value: float


class PeakInfo:
    """ Class holding information about individual peaks.
        Conforms to QualityParameterInfo protocol
    """
    def __init__(self, number: int, start_position: float, end_position: float,
                 width: float, value: float) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.width = width
        self.value = value


class AveragesInfo:
    """ Class holding information about piecewise averages.
        Conforms to QualityParameterInfo protocol
    """
    def __init__(self, number: int, start_position: float, end_position: float,
                 width: float, value: float) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.width = width
        self.value = value


class ScatterInfo:
    """ Class holding information about piecewise scatter characteristics.
        Conforms to QualityParameterInfo protocol
    """
    def __init__(self, number: int, start_position: float, end_position: float,
                 width: float, value: float) -> None:
        self.number = number
        self.start_position = start_position
        self.end_position = end_position
        self.width = width
        self.value = value


class TapeSpecs(NamedTuple):
    """ Tuple holding information about tape specifications
    """
    width: float
    min_average: float
    min_value: float
    average_length: float


class TapeProduct(Enum):
    """ Enum summarizing different tape specifications
    """
    SUPERLINK_PHASE = TapeSpecs(width=3.0,
                                min_average=135.0,
                                min_value=70.0,
                                average_length=20.0)
    SUPERLINK_NEUTRAL = TapeSpecs(width=6.0,
                                  min_average=200.0,
                                  min_value=100.0,
                                  average_length=20.0)
    STANDARD = TapeSpecs(width=12.0,
                         min_average=700.0,
                         min_value=500.0,
                         average_length=20.0)


class FailType(Enum):
    """ Enum of different failur types.

    Args:
        Enum (str): failure tape as string
    """
    AVERAGE = 'Average Failed'
    SCATTER = 'Scatter Failed'
    MINIMUM = 'Minimum Failed'
    DROP_OUT = 'Drop Out Failed'


class FailInformation(NamedTuple):
    """ Tuple of failure information
    """
    type: FailType
    quality_parameter_info: QualityParameterInfo
    description: str


class QualityReport(NamedTuple):
    """ Class containing all information for a quality report for a tape.
    """
    tape_id: str
    passed: bool
    fail_information: Optional[List[FailInformation]]
