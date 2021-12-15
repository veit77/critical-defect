from typing import List
import pandas as pd
from scipy.signal import find_peaks, peak_widths
from quality_data_types import PeakInfo, AveragesInfo


class TapeQualityInformation:
    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @data.setter
    def data(self, value) -> None:
        if not isinstance(value, pd.DataFrame) or value is None:
            raise TypeError("Wrong data type for data")

        self._data = value

    tape_id = str

    expected_average: float
    expected_average_length: float

    @property
    def peak_definition(self) -> float:
        return self.expected_average * 0.8

    averages: List[AveragesInfo]
    peak_info: List[PeakInfo]

    def __init__(self, data: pd.DataFrame, tape_id: str,
                 expected_average: float, expected_average_length: float):
        self.data = data
        self.tape_id = tape_id
        self.expected_average = expected_average
        self.expected_average_length = expected_average_length
        self.peak_info = []
        self.averages = []
        self.data_plot = None

    @staticmethod
    def load_data(from_path: str,
                  convert_to_meters: bool = False) -> pd.DataFrame:
        """ Loads csv-data from TapeStar Ic-exports.

        Args:
            from_path (str): Path of csv-file to be loaded
            convert_to_meters (bool, optional): Convert postions from mm to meters. Defaults to False.

        Returns:
            pd.DataFrame: Ic-data from TapeStar csv-file
        """
        data = pd.read_csv(from_path, header=1, delimiter="\t")

        if convert_to_meters:
            data.iloc[:, 0] = data.iloc[:, 0].div(1000.0)
        return data

    def calculate_averages(self) -> None:
        threshold = self.expected_average * 0.8
        above_threshold_list = self.data.index[
            self.data.iloc[:, 1] > threshold].to_list()
        start_index = above_threshold_list[0]
        end_index = above_threshold_list[-1]

        next_position = (self.data.iloc[start_index, 0] +
                         self.expected_average_length)
        last_index = start_index
        piece = 0

        # works only if positions are counting up
        # TODO: reverse order if counting down?
        while next_position < self.data.iloc[end_index, 0]:
            next_index = self.data.index[
                self.data.iloc[:, 0] > next_position].to_list()[0]
            average = self.data.iloc[last_index:next_index, 1].mean()
            average_info = AveragesInfo(
                number=piece,
                start_position=self.data.iloc[last_index, 0],
                end_position=self.data.iloc[next_index, 0],
                width=self.data.iloc[next_index, 0] - self.data.iloc[last_index, 0],
                value=average)
            self.averages.append(average_info)
            last_index = next_index
            next_position += self.expected_average_length
            piece += 1

        # append averages till end of tape
        average = self.data.iloc[last_index:end_index, 1].mean()
        average_info = AveragesInfo(
            number=piece,
            start_position=self.data.iloc[last_index, 0],
            end_position=self.data.iloc[next_index, 0],
            width=self.data.iloc[next_index, 0] - self.data.iloc[last_index, 0],
            value=average)
        self.averages.append(average_info)

        print(f"Start: {start_index}, {self.data.iloc[start_index, 0]}")

    def calculate_basic_peak_info(self):
        indices, _ = find_peaks(-self.data.iloc[:, 1],
                                height=(-self.peak_definition, 0),
                                distance=10)
        widths = peak_widths(self.data.iloc[:, 1], indices)

        info: List[PeakInfo] = []
        for i, index in enumerate(indices):
            info.append(
                PeakInfo(number=i,
                         start_position=self.data.iloc[index, 0],
                         end_position=self.data.iloc[index, 0],
                         width=widths[0][i],
                         value=self.data.iloc[index, 1]))

        self.peak_info = info

    # TODO missing implementation
    def peak_fwhm(self, position: int) -> float:
        return 0.0

    # TODO missing implementation
    def write_peak_info(self, to_path: str) -> None:
        for info in self.peak_info:
            print(f"x={info.start_position}, width={info.width}")
