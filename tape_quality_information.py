""" Class implementation for TapeQualityInformation
"""

from typing import List, Optional
from math import isclose
from pandas import DataFrame
from scipy.signal import find_peaks
from quality_data_types import PeakInfo, AveragesInfo


class TapeQualityInformation:
    """ Class to collect information on quality features of HTS tapes

    Attributes:
    -----------
    data : DataFrame
        Critical current vs. position data of a HTS tape.
    tape_id: str
        ID of the HTS tape
    expected_average : Optional[float]
        Approximate average critical current. Used for drop-out detection and
        piecewise average calculation.
    averaging_length : Optional[float]
        Tape length over which to average. Used for piecewise average
        calculation.
    averages : List[AveragesInfo] = []
        Piecewise averages.
    drop_outs : List[PeakInfo] = []
        Information about all drop-outs.

    Methods:
    --------
    calculate_averages(self, data: DataFrame) -> List[AveragesInfo]
        Calculates piecewise averages.
    calculate_drop_out_info(self, data: DataFrame) -> List[PeakInfo]
        Calculate drop-out information.
    """
    @property
    def data(self) -> DataFrame:
        return self._data

    @data.setter
    def data(self, value) -> None:
        if not isinstance(value, DataFrame) or value is None:
            raise TypeError("Wrong data type for data")
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")
        if self.averaging_length is None:
            raise ValueError("Property expected_average_length not set")

        self._data = value
        self.calculate_averages()
        self.calculate_drop_out_info()

    tape_id = str

    expected_average: Optional[float]
    averaging_length: Optional[float]

    averages: List[AveragesInfo] = []
    drop_outs: List[PeakInfo] = []

    @property
    def _peak_definition(self) -> float:
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")
        return self.expected_average * 0.8

    def __init__(self, data: DataFrame, tape_id: str, expected_average: float,
                 expected_average_length: float):
        self.expected_average = expected_average
        self.averaging_length = expected_average_length

        self.data = data
        self.tape_id = tape_id

    def calculate_averages(self) -> None:
        """ Calculates piecewise averages.

        Raises:
            ValueError: throws exception if expected_average and
                averaging_length are not properly set.
        """
        if self.averaging_length is None:
            raise ValueError("Property expected_average_length not set")

        start_index, end_index = self._find_start_end_index(self.data)
        length = self.averaging_length

        next_position = (self.data.iloc[start_index, 0] + length)
        last_index = start_index
        piece = 0
        averages_info_list = []

        # works only if positions are counting up
        # TODO: reverse order if counting down?

        # Calculate averages and store them in AveragesInfo instance
        while next_position < self.data.iloc[end_index, 0]:
            next_index = self.data.index[
                self.data.iloc[:, 0] > next_position].to_list()[0]
            average = self.data.iloc[last_index:next_index, 1].mean()
            start_position = self.data.iloc[last_index, 0]
            end_position = self.data.iloc[next_index, 0]
            average_info = AveragesInfo(number=piece,
                                        start_position=start_position,
                                        end_position=end_position,
                                        value=average)
            averages_info_list.append(average_info)
            last_index = next_index
            next_position += length
            piece += 1

        # append averages till end of tape
        average = self.data.iloc[last_index:end_index, 1].mean()
        start_position = self.data.iloc[last_index, 0]
        end_position = self.data.iloc[end_index, 0]
        average_info = AveragesInfo(number=piece,
                                    start_position=start_position,
                                    end_position=end_position,
                                    value=average)
        averages_info_list.append(average_info)
        self.averages = averages_info_list

    def calculate_drop_out_info(self, pos_tol: float = 2e-3) -> None:
        """ Calculate drop-out information.

        Args:
            pos_tol (float): Tolerance for position to be identified as the same.
        """
        start_index, end_index = self._find_start_end_index(self.data)
        indices, _ = find_peaks(-self.data.iloc[:, 1],
                                height=(-self._peak_definition, 0),
                                distance=10)

        # Remove all drop-outs not on the actual tape
        indices = list(filter(lambda x: x >= start_index, indices))
        indices = list(filter(lambda x: x <= end_index, indices))

        peak_info_list: List[PeakInfo] = []
        last_peak = PeakInfo()
        for i, index in enumerate(indices):
            position = self.data.iloc[index, 0]
            value = self.data.iloc[index, 1]
            level = self.expected_average
            for average in self.averages:
                if (position > average.start_position
                        and position < average.end_position):
                    level = average.value
                    break

            half_max = (value + level) / 2.0
            start_position = self.data.iloc[start_index, 0]
            end_position = self.data.iloc[end_index, 0]
            for j in range(index, len(self.data.index)):
                if self.data.iloc[j, 1] > half_max:
                    end_position = self.data.iloc[j, 0]
                    break
            for j in range(index, 0, -1):
                if self.data.iloc[j, 1] > half_max:
                    start_position = self.data.iloc[j, 0]
                    break

            current_peak = PeakInfo(number=i,
                                    start_position=start_position,
                                    end_position=end_position,
                                    center_position=position,
                                    value=value)

            # check if width is the same. if value smaler than before, remove
            # last entry and replace by new entry. Add new entry, if not the
            # same width (tolerance is 2mm -> might be tweaked a bit)
            if (isclose(start_position, last_peak.start_position, abs_tol=pos_tol)
                    and isclose(end_position, last_peak.end_position, abs_tol=pos_tol)):
                if value < last_peak.value:
                    peak_info_list.remove(last_peak)
                    peak_info_list.append(current_peak)
                    last_peak = current_peak
            else:
                peak_info_list.append(current_peak)
                last_peak = current_peak

        self.drop_outs = peak_info_list

    def _find_start_end_index(self, data: DataFrame) -> tuple[int, int]:
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")

        threshold = self.expected_average * 0.8

        # Find start and end of tape -> where Ic is greater threshold
        # the first time and last time, respectively.
        above_threshold_list = data.index[data.iloc[:, 1] > threshold].to_list()
        start_index = above_threshold_list[0]
        end_index = above_threshold_list[-1]

        return start_index, end_index
