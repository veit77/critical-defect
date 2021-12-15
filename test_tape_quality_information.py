import pytest
import tape_quality_information as di
from quality_data_types import TapeProduct


def test_data_setter_raises():
    tape_spec = TapeProduct.STANDARD.value
    with pytest.raises(TypeError, match=r"Wrong data type for data"):
        _ = di.TapeQualityInformation(10.0, 'id', tape_spec.min_average,
                                      tape_spec.average_length)
