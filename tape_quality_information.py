from typing import List, Optional
from pandas import DataFrame
from math import isclose
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
        Approximate average critical current. Used for drop-out detection and piecewise average calculation.
    averaging_length : Optional[float]
        Tape length over which to average. Used for piecewise average calculation.
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
        self.averages = self.calculate_averages(self._data)
        self.drop_outs = self.calculate_drop_out_info(self._data)

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

    def calculate_averages(self, data: DataFrame) -> List[AveragesInfo]:
        """ Calculates piecewise averages.

        Args:
            data (DataFrame): Pandas DataFrame containing Ic vs. position data.

        Raises:
            ValueError: throws exception if expected_average and averaging_length are not properly set.

        Returns:
            List[AveragesInfo]: List of information about piecewise averages.
        """
        if self.averaging_length is None:
            raise ValueError("Property expected_average_length not set")

        start_index, end_index = self._find_start_end_index_of_tape(data)
        length = self.averaging_length

        next_position = (data.iloc[start_index, 0] + length)
        last_index = start_index
        piece = 0
        averages_info_list = []

        # works only if positions are counting up
        # TODO: reverse order if counting down?
        # Calculate averages and store them in AveragesInfo instance
        while next_position < data.iloc[end_index, 0]:
            next_index = data.index[data.iloc[:,
                                              0] > next_position].to_list()[0]
            average = data.iloc[last_index:next_index, 1].mean()
            start_position = data.iloc[last_index, 0]
            end_position = data.iloc[next_index, 0]
            average_info = AveragesInfo(number=piece,
                                        start_position=start_position,
                                        end_position=end_position,
                                        value=average)
            averages_info_list.append(average_info)
            last_index = next_index
            next_position += length
            piece += 1

        # append averages till end of tape
        average = data.iloc[last_index:end_index, 1].mean()
        start_position = data.iloc[last_index, 0]
        end_position = data.iloc[end_index, 0]
        average_info = AveragesInfo(number=piece,
                                    start_position=start_position,
                                    end_position=end_position,
                                    value=average)
        averages_info_list.append(average_info)
        return averages_info_list

    # TODO Function should not take an argument that is a member of the class
    # and should not return
    def calculate_drop_out_info(self, data: DataFrame) -> List[PeakInfo]:
        """ Calculate drop-out information.

        Args:
            data (DataFrame): Pandas DataFrame containing Ic vs. position data.

        Returns:
            List[PeakInfo]: List of information about drop-outs.
        """
        start_index, end_index = self._find_start_end_index_of_tape(data)
        indices, _ = find_peaks(-data.iloc[:, 1],
                                height=(-self._peak_definition, 0),
                                distance=10)

        # Remove all drop-outs not on the actual tape
        indices = list(filter(lambda x: x >= start_index, indices))
        indices = list(filter(lambda x: x <= end_index, indices))

        peak_info_list: List[PeakInfo] = []
        last_peak = PeakInfo()
        for i, index in enumerate(indices):
            position = data.iloc[index, 0]
            value = data.iloc[index, 1]
            level = self.expected_average
            for average in self.averages:
                if position > average.start_position and position < average.end_position:
                    level = average.value
                    break

            half_max = (value + level) / 2.0
            start_position = 0.0
            end_position = 0.0
            for j in range(index, len(data.index)):
                if data.iloc[j, 1] > half_max:
                    end_position = data.iloc[j, 0]
                    break
            for j in range(index, 0, -1):
                if data.iloc[j, 1] > half_max:
                    start_position = data.iloc[j, 0]
                    break

            current_peak = PeakInfo(number=i,
                                    start_position=start_position,
                                    end_position=end_position,
                                    center_position=position,
                                    value=value)

            # check if width is the same. if value smaler than before, remove
            # last entry and replace by new entry. Add new entry, if not the
            # same width (tolerance is 2mm -> might be tweaked a bit)
            if (isclose(start_position, last_peak.start_position, abs_tol=2e-3)
                and isclose(end_position, last_peak.end_position, abs_tol=2e-3)):
                if value < last_peak.value:
                    peak_info_list.remove(last_peak)
                    peak_info_list.append(current_peak)
                    last_peak = current_peak
            else:
                peak_info_list.append(current_peak)
                last_peak = current_peak

        return peak_info_list

    def _find_start_end_index_of_tape(self,
                                      data: DataFrame) -> tuple[int, int]:
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")

        threshold = self.expected_average * 0.8

        # Find start and end of tape -> where Ic is greater threshold
        # the first time and last time, respectively.
        above_threshold_list = data.index[data.iloc[:,
                                                    1] > threshold].to_list()
        start_index = above_threshold_list[0]
        end_index = above_threshold_list[-1]

        return start_index, end_index
