""" Helper functions for TapeStar quality assessment.
"""
from typing import Optional
from pandas import DataFrame, read_csv


def load_data(from_path: str,
              convert_to_meters: Optional[bool] = False) -> DataFrame:
    """ Loads csv-data from TapeStar Ic-exports.

    Args:
        from_path (str): Path of csv-file to be loaded
        convert_to_meters (bool, optional): Convert postions from mm to
            meters. If None, guess whether it's necessary to convert.
            Defaults to False.

    Returns:
        DataFrame: Ic-data from TapeStar csv-file
    """
    data = read_csv(from_path, header=1, delimiter="\t")

    convert = convert_to_meters

    # convert to meters if number of data points is close to length
    if convert_to_meters is None:
        length = abs(data.iloc[:, 0].values[-1] - data.iloc[:, 0].values[0])
        convert = data.iloc[:, 0].size/length < 10

    if convert:
        data.iloc[:, 0] = data.iloc[:, 0].div(1000.0)
    return data
