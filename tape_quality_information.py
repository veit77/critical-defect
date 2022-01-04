""" Class implementation for TapeQualityInformation
"""

from typing import List, Optional
from math import isclose
from pandas import DataFrame
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from quality_data_types import PeakInfo, AveragesInfo, TapeSection


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
    dropouts : List[PeakInfo] = []
        Information about all drop-outs.

    Methods:
    --------
    calculate_averages() -> None
        Calculates piecewise averages.
    calculate_drop_out_info() -> None
        Calculate drop-out information.
    """
    @property
    def data(self) -> DataFrame:
        return self._data

    @data.setter
    def data(self, value: DataFrame) -> None:
        if not isinstance(value, DataFrame) or value is None:
            raise TypeError("Wrong data type for data")
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")

        # reverse order of dataframe if end position is smaller than start
        # position.
        if value.iloc[0, 0] > value.iloc[-1, 0]:
            self._data = value.iloc[::-1].reset_index(drop=True)
        else:
            self._data = value

        try:
            self.calculate_averages()
        except ValueError as error:
            print(f"Error: Calculating averages failed: {repr(error)}")
        self.calculate_drop_out_info()

    @property
    def tape_section(self) -> TapeSection:
        start, end = self._find_start_end_index(self._data)
        start_pos = self._data.iloc[start, 0]
        end_pos = self._data.iloc[end, 0]
        return TapeSection(start_pos, end_pos)

    tape_id = str

    expected_average: float
    averaging_length: Optional[float]

    averages: Optional[List[AveragesInfo]] = []
    dropouts: List[PeakInfo] = []

    @property
    def _peak_definition(self) -> float:
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")
        return self.expected_average * 0.8

    def __init__(self, data: DataFrame, tape_id: str, expected_average: float,
                 averaging_length: Optional[float]):
        self.expected_average = expected_average
        self.averaging_length = averaging_length
        self.tape_id = tape_id

        # Always set data after expected_average and averaging_length is set.
        self.data = data

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

        # Calculate averages and store them in AveragesInfo instance
        while next_position < self.data.iloc[end_index, 0]:
            next_index = self.data.index[
                self.data.iloc[:, 0] > next_position].to_list()[0]
            average = self.data.iloc[last_index:next_index, 1].mean()
            start_position = self.data.iloc[last_index, 0]
            end_position = self.data.iloc[next_index, 0]
            average_info = AveragesInfo(id=piece,
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
        average_info = AveragesInfo(id=piece,
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
            if self.averages is not None:
                for average in self.averages:
                    if (position > average.start_position
                            and position < average.end_position):
                        level = average.value
                        break

            half_max = (value + level) / 2.0
            start_position = self._find_half_max_position(index, half_max, False)
            end_position = self._find_half_max_position(index, half_max, True)

            current_peak = PeakInfo(id=i,
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

        self.dropouts = peak_info_list

    def _find_half_max_position(self, peak_index: int, half_max: float,
                                go_up: bool) -> float:
        half_max_position = 0.0
        last_index = len(self.data.index) - 1
        step = 1
        if not go_up:
            last_index = 0
            step = -1

        half_max_position = self.data.iloc[last_index, 0]
        for j in range(peak_index, last_index, step):
            if self.data.iloc[j, 1] > half_max:
                x_values = [self.data.iloc[j, 0], self.data.iloc[j-step, 0]]
                y_values = [self.data.iloc[j, 1], self.data.iloc[j-step, 1]]
                f_of_y = interp1d(y_values, x_values)
                half_max_position = f_of_y(half_max)[()]
                break

        return half_max_position

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
