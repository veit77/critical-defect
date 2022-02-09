""" Definition of different HTS tape products
"""
from enum import Enum
from math import exp
from .data_types import TapeSpecs


class TapeProduct(Enum):
    """ Enum summarizing different tape specifications
    """
    SUPERLINK_PHASE = TapeSpecs(
        width=3.0,
        min_tape_length=190.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=lambda ic: 1.43587 * exp(0.027726 * ic),
        width_from_true_baseline=False,
        min_average=135.0,
        averaging_length=1.0,
        description="SuperLink Phase")
    SUPERLINK_NEUTRAL = TapeSpecs(
        width=6.0,
        min_tape_length=190.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=lambda ic: 1.43587 * exp(0.027726 * ic),
        min_average=180.0,
        width_from_true_baseline=False,
        averaging_length=1.0,
        description="SuperLink Neutral")
    SUPERLINK_PHASE_TEST = TapeSpecs(
        width=3.0,
        min_tape_length=50.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=lambda ic: 1.43587 * exp(0.027726 * ic),
        width_from_true_baseline=False,
        min_average=135.0,
        averaging_length=1.0,
        description="SuperLink Phase")
    STANDARD1 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=None,
                          dropout_func=None,
                          width_from_true_baseline=True,
                          min_average=None,
                          averaging_length=None,
                          description="Standard Tape 1")
    STANDARD2 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=None,
                          dropout_func=None,
                          width_from_true_baseline=True,
                          min_average=700.0,
                          averaging_length=20.0,
                          description="Standard Tape 2")
    STANDARD3 = TapeSpecs(width=12.0,
                          min_tape_length=25.0,
                          min_value=500.0,
                          dropout_value=150.0,
                          dropout_func=lambda x: 20,
                          width_from_true_baseline=True,
                          min_average=700.0,
                          averaging_length=20.0,
                          description="Standard Tape 3")
