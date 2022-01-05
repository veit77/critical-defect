""" Helper functions for TapeStar quality assessment.
"""
from pandas import DataFrame, read_csv


def load_data(from_path: str,
                  convert_to_meters: bool = False) -> DataFrame:
    """ Loads csv-data from TapeStar Ic-exports.

    Args:
        from_path (str): Path of csv-file to be loaded
        convert_to_meters (bool, optional): Convert postions from mm to
            meters. Defaults to False.

    Returns:
        DataFrame: Ic-data from TapeStar csv-file
    """
    data = read_csv(from_path, header=1, delimiter="\t")

    if convert_to_meters:
        data.iloc[:, 0] = data.iloc[:, 0].div(1000.0)
    return data
