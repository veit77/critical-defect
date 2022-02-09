import pytest
import pandas
import quality_assessment.quality_assessor as qa
from quality_assessment.products import TapeProduct
from quality_assessment.tape_quality_information import TapeQualityInformation


def test_save_pdf_raises_value_error():
    tape_spec = TapeProduct.STANDARD3.value
    data = {'x': [1, 2, 3, 4], 'y': [20, 21, 19, 18]}
    quality_info = TapeQualityInformation(pandas.DataFrame(data), "ID", 0.0)
    assessor = qa.TapeQualityAssessor(quality_info, tape_spec)
    dirname = "./unknown_directory"
    with pytest.raises(ValueError, match=f"Directory {dirname} does not exist"):
        assessor.save_pdf_report(dirname)
