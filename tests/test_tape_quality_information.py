import pytest
import pandas as pd
import quality_assessor.tape_quality_information as di
from quality_assessor.products import TapeProduct


def test_data_setter_raises_type_error():
    tape_spec = TapeProduct.STANDARD3.value
    with pytest.raises(TypeError, match=r"Wrong data type for data"):
        _ = di.TapeQualityInformation(10.0, 'id', tape_spec.min_average,
                                      tape_spec.average_length)


@pytest.mark.parametrize("exception_text,average_value,length_value", [
    pytest.param(r"Property expected_average not set", None,
                 TapeProduct.STANDARD3.value.average_length)
])
def test_data_setter_raises_value_error(exception_text: str,
                                        average_value: float,
                                        length_value: float):
    with pytest.raises(ValueError, match=exception_text):
        _ = di.TapeQualityInformation(pd.DataFrame(), 'id', average_value,
                                      length_value)
