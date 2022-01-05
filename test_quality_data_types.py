import pytest
from quality_data_types import QualityReport, TestType


def test_qualityreport_init():
    report = QualityReport("my_id", TestType.AVERAGE, [])
    assert report.fail_information is None