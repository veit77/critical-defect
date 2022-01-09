import pytest
from quality_data_types import (QualityReport, TestType, PeakInfo,
                                AveragesInfo, ScatterInfo, QualityParameterInfo)


def test_qualityreport_init():
    report = QualityReport("my_id", TestType.AVERAGE, [])
    assert report.fail_information is None


def test_peakinfo_conforms_protocoll():
    info = PeakInfo()
    assert isinstance(info, QualityParameterInfo)


def test_averagesinfo_conforms_protocoll():
    info = AveragesInfo()
    assert isinstance(info, QualityParameterInfo)


def test_scatterinfo_conforms_protocoll():
    info = ScatterInfo()
    assert isinstance(info, QualityParameterInfo)
