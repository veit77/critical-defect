""" provides data types for analysing defect structures in HTS tapes
"""
from typing import Optional, Protocol, Callable
from dataclasses import dataclass
from enum import Enum
from math import exp


class QualityParameterInfo(Protocol):
    """ Protocol for defect information

     Attributes:
    ------------
        id (int): ID of the defect
        start_position (float): Start position of the defect.
        end_position (float): End position of the defect.
        center_position (float): Center position of the defect.
        width (float): Width of the defect section.
        value (float): Value of the defect.
        description (str): Description of the defect information
    """
    id: int
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
                 id: int = 1,
                 start_position: float = 0.0,
                 end_position: float = 0.0,
                 center_position: float = 0.0,
                 value: float = 0.0) -> None:
        self.id = id
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
                 id: int = 0,
                 start_position: float = 0.0,
                 end_position: float = 0.0,
                 value: float = 0.0) -> None:
        self.id = id
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

    def __init__(self, id: int, start_position: float, end_position: float,
                 value: float) -> None:
        self.id = id
        self.start_position = start_position
        self.end_position = end_position
        self.value = value


@dataclass
class TapeSpecs():
    """ Tuple holding information about tape specifications

    Attributes:
    -----------
        width (float): Tape width in mm
        min_tape_length (float): Minimum tape length for product in m
        min_value (float): Minimum value in A
        dropout_value (Optional[float]): Minimum drop-out value in A
        dropout_func (Optional[Callable[[float], float]]): Maximum width of drop-out in mm
        min_average (Optional[float]): Minimum average value in A
        average_length (Optional[float]): Length over which to average in m
        description (str): Name/Description of the product
    """
    width: float
    min_tape_length: float
    min_value: float
    dropout_value: Optional[float]
    dropout_func: Optional[Callable[[float], float]]
    min_average: Optional[float]
    average_length: Optional[float]
    description: str


class TapeProduct(Enum):
    """ Enum summarizing different tape specifications
    """
    SUPERLINK_PHASE = TapeSpecs(width=3.0,
                                min_tape_length=190.0,
                                min_value=100.0,
                                dropout_value=20.0,
                                dropout_func=lambda ic: 2.5 + 7.5/50*(ic-20),
                                min_average=135.0,
                                average_length=20.0,
                                description="SuperLink Phase")
    SUPERLINK_PHASE_TEST = TapeSpecs(
        width=3.0,
        min_tape_length=190.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=lambda ic: 1.43587 * exp(0.027726 * ic),
        min_average=135.0,
        average_length=20.0,
        description="SuperLink Phase Test")
    SUPERLINK_NEUTRAL = TapeSpecs(width=6.0,
                                  min_average=200.0,
                                  min_value=100.0,
                                  dropout_value=50.0,
                                  dropout_func=None,
                                  average_length=20.0,
                                  min_tape_length=190.0,
                                  description="SuperLink Neutral")
    STANDARD1 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=None,
                          dropout_func=None,
                          min_average=None,
                          average_length=None,
                          description="Standard Tape 1")
    STANDARD2 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=None,
                          dropout_func=None,
                          min_average=700.0,
                          average_length=20.0,
                          description="Standard Tape 2")
    STANDARD3 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=150.0,
                          dropout_func=lambda x: 20,
                          min_average=700.0,
                          average_length=20.0,
                          description="Standard Tape 3")


class TestType(Enum):
    """ Enum of different quality test types.
    """
    AVERAGE = 'Average Value'
    SCATTER = 'Scatter'         # TODO Currently not available in Specs and Tests
    MINIMUM = 'Minimum Value'
    DROPOUT = 'Drop Out'


@dataclass
class TapeSection:
    """ Holds information of tape sections.

    Attributes:
    -----------
        start_position (float): Start position of the tape section.
        end_position (float): End position of the tape section.
        length (float, read only): Length of the tape section.
    """
    @property
    def length(self) -> float:
        return self.end_position - self.start_position

    start_position: float
    end_position: float


@dataclass
class QualityReport:
    """ Class containing all information for a quality report for a tape
        regarding a specific quality parameter.

    Attributes:
    -----------
        tape_id (str): ID of the tested tape.
        test_type (TestType): Type of the test.
        fail_information (Optional[list[QualityParameterInfo]]): Information about failures
        passed (bool): Test passed or not.
    """
    tape_id: str
    test_type: TestType
    fail_information: Optional[list[QualityParameterInfo]] = None

    @property
    def passed(self) -> bool:
        return self.fail_information is None

    def __post_init__(self):
        # if list is empty, set fail_information to None
        if not self.fail_information:
            self.fail_information = None
