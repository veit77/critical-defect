from typing import List, Optional
from pandas import DataFrame
from scipy.signal import find_peaks, peak_widths
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

    def __init__(self, data: DataFrame, tape_id: str,
                 expected_average: float, expected_average_length: float):
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
        if self.expected_average is None:
            raise ValueError("Property expected_average not set")
        if self.averaging_length is None:
            raise ValueError("Property expected_average_length not set")

        threshold = self.expected_average * 0.8
        length = self.averaging_length

        # Find start and end of tape -> where Ic is greater threshold the first time and last time, respectively.
        above_threshold_list = data.index[
            data.iloc[:, 1] > threshold].to_list()
        start_index = above_threshold_list[0]
        end_index = above_threshold_list[-1]

        next_position = (data.iloc[start_index, 0] + length)
        last_index = start_index
        piece = 0
        averages_info_list = []

        # works only if positions are counting up
        # TODO: reverse order if counting down?
        # Calculate averages and store them in AveragesInfo instance
        while next_position < data.iloc[end_index, 0]:
            next_index = data.index[data.iloc[:, 0] > next_position].to_list()[0]
            average = data.iloc[last_index:next_index, 1].mean()
            average_info = AveragesInfo(
                number=piece,
                start_position=data.iloc[last_index, 0],
                end_position=data.iloc[next_index, 0],
                width=data.iloc[next_index, 0] - data.iloc[last_index, 0],
                value=average)
            averages_info_list.append(average_info)
            last_index = next_index
            next_position += length
            piece += 1

        # append averages till end of tape
        average = data.iloc[last_index:end_index, 1].mean()
        average_info = AveragesInfo(
            number=piece,
            start_position=data.iloc[last_index, 0],
            end_position=data.iloc[next_index, 0],
            width=data.iloc[next_index, 0] - data.iloc[last_index, 0],
            value=average)
        averages_info_list.append(average_info)
        return averages_info_list

    def calculate_drop_out_info(self, data: DataFrame) -> List[PeakInfo]:
        """ Calculate drop-out information.

        Args:
            data (DataFrame): Pandas DataFrame containing Ic vs. position data.

        Returns:
            List[PeakInfo]: List of information about drop-outs.
        """
        indices, _ = find_peaks(-data.iloc[:, 1],
                                height=(-self._peak_definition, 0),
                                distance=10)
        # TODO Width calculation not working. Replace by _peak_fwhm.
        widths = peak_widths(data.iloc[:, 1], indices)

        peak_info_list: List[PeakInfo] = []
        for i, index in enumerate(indices):
            peak_info_list.append(
                PeakInfo(number=i,
                         start_position=data.iloc[index, 0],
                         end_position=data.iloc[index, 0],
                         width=widths[0][i],
                         value=data.iloc[index, 1]))

        return peak_info_list

    # TODO missing implementation
    # TODO Attention: Multiple peaks can have the same start and end position and the same fwhm.
    def _peak_fwhm(self, position: int) -> float:
        return 0.0

    # TODO missing implementation -> still needed ?
    def write_peak_info(self, to_path: str) -> None:
        for info in self.drop_outs:
            print(f"x={info.start_position}, width={info.width}")
