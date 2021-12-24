""" Class implementation for TapeQualityAssessor
"""

from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame, read_csv
from quality_data_types import (QualityReport, FailType, TapeSpecs, TapeSection,
                                TapeProduct, QualityParameterInfo)
from tape_quality_information import TapeQualityInformation
from quality_pdf_report import ReportPDFCreator


class TapeQualityAssessor():
    """ Class for assessing whether specs for various quality parameters are met.
    """
    tape_quality_info: TapeQualityInformation
    tape_specs: TapeSpecs
    quality_reports: List[QualityReport] = []
    ok_tape_sections: List[TapeSection] = []

    def __init__(self, tape_quality_info, tape_specs) -> None:
        self.tape_quality_info = tape_quality_info
        self.tape_specs = tape_specs
        self.quality_reports = []
        self.data_plot = None

    @staticmethod
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

    def assess_meets_specs(self) -> None:
        """ Kicks off assessment for various quality parameters and stores
            quality reports.
        """
        self.quality_reports.append(self.assess_average_value())
        self.quality_reports.append(self.assess_min_value())

    def determine_ok_tape_section(self, min_length: float) -> None:
        tape_sections = [self.tape_quality_info.tape_section]

        for q_report in self.quality_reports:
            if q_report.fail_information is None:
                continue
            for fail_info in q_report.fail_information:
                # TODO if defect spans over two sections, this defect is not cut out
                section_to_devide = [
                    section for section in tape_sections
                    if section.start_position <= fail_info.start_position
                    and section.end_position > fail_info.end_position
                ]
                if section_to_devide:
                    tape_sections.remove(section_to_devide[0])
                    new_sections = self._devide_tape_section(
                        section_to_devide[0], fail_info.start_position,
                        fail_info.end_position)
                    tape_sections.append(new_sections[0])
                    tape_sections.append(new_sections[1])

        tape_sections = [
            tape_sec for tape_sec in tape_sections
            if tape_sec.length >= min_length
        ]

        self.ok_tape_sections = tape_sections

    def save_pdf_report(self) -> None:
        """ Creates PDF report for the tape and saves it.
        """
        pdf_report = ReportPDFCreator(self._make_plot(), self.quality_reports)
        pdf_report.create_report()
        pdf_report.save_report("tuto2.pdf")

    def plot_defects(self) -> None:
        """ Shows self.data_plot in a window.
        """
        _ = self._make_plot()

        plt.show()

    def print_reports(self):
        """ print all available quality reports to the shell.
        """
        for report in self.quality_reports:
            print(f"Tape {report.tape_id} passed: {report.passed}")
            if not report.passed and report.fail_information is not None:
                if report.type is not None:
                    print(f"Failed due to: {report.type.value}")
                else:
                    print("Failed for unknown reason")
                for fail_info in report.fail_information:
                    print(fail_info.description)

    def assess_average_value(self) -> QualityReport:
        """ Assesses if average value meet the specs.

        Returns:
            QualityReport: Quality report on average values.
        """
        return self._assess_failure(FailType.AVERAGE,
                                    self.tape_specs.min_average,
                                    self.tape_quality_info.averages)

    def assess_min_value(self) -> QualityReport:
        """ Assesses if minimum values meet the specs.

        Returns:
            QualityReport: Quality report on minimum values.
        """
        return self._assess_failure(FailType.MINIMUM,
                                    self.tape_specs.min_value,
                                    self.tape_quality_info.drop_outs)

    def _assess_failure(
            self, fail_type: FailType, threshold: float,
            parameter_infos: List[QualityParameterInfo]) -> QualityReport:
        """ Assesses if selected quality parameter meets the specs.

        Args:
            fail_type (FailType): Qualityparameter to assess.
            threshold (float): threshold to pass specs.
            parameter_infos (List[QualityParameterInfo])

        Returns:
            QualityReport: Quality report on selected quality parameter.
        """

        fails = [p_info for p_info in parameter_infos if p_info.value < threshold]

        if not fails:
            return QualityReport(self.tape_quality_info.tape_id, True)
        else:
            return QualityReport(self.tape_quality_info.tape_id, False,
                                 fail_type, fails)

    # TODO prevent opening of empty window on creation of figure
    def _make_plot(self) -> Figure:
        data = self.tape_quality_info.data
        fig = plt.figure(figsize=(9.5, 3.1))
        axis = fig.subplots()
        axis.plot(data.iloc[:, 0], data.iloc[:, 1], label='Data')

        # plot fail reports
        for report in self.quality_reports:
            if report.fail_information is None:
                continue
            for fail in report.fail_information:
                x = [
                    fail.start_position,
                    fail.end_position
                ]
                y = [
                    fail.value,
                    fail.value
                ]

                if report.type == FailType.AVERAGE:
                    color = 'crimson'
                    axis.plot(x, y,
                              color=color,
                              marker='|',
                              linewidth=2.0,
                              label='Averages Failed')
                elif report.type == FailType.MINIMUM:
                    color = 'deeppink'
                    axis.scatter([fail.center_position],
                                 [fail.value],
                                 color=color,
                                 s=15,
                                 marker='D',
                                 label='Minimum Failed')
                    axis.plot(x, y,
                              color=color,
                              marker='|',
                              linewidth=2.0,
                              label='Averages Failed')

        # axis.legend()
        plt.xlabel("Position (m)")
        plt.ylabel("Critical Current (A)")
        axis.grid()

        return fig

    def _devide_tape_section(self, tape_section: TapeSection, cut_from: float,
                             cut_to: float) -> List[TapeSection]:
        section1 = TapeSection(tape_section.start_position, cut_from)
        section2 = TapeSection(cut_to, tape_section.end_position)
        return [section1, section2]


def main():
    product = TapeProduct.STANDARD.value
    quality_info = [
        TapeQualityInformation(
            TapeQualityAssessor.load_data("data/20204-X-10_500A.dat", False),
            "20204-X-10", product.min_average, product.average_length),
        TapeQualityInformation(
            TapeQualityAssessor.load_data(
                "data/17346-X-11-BL_30_29970_500A.dat", True), "17346-X-11",
            product.min_average, product.average_length)
    ]

    for q_info in quality_info:
        assessor = TapeQualityAssessor(q_info, product)
        assessor.tape_quality_info = q_info

        assessor.assess_meets_specs()
        assessor.determine_ok_tape_section(product.min_tape_length)

        assessor.save_pdf_report()
        assessor.print_reports()
        assessor.plot_defects()

        print("OK Tape Sections:")
        for i, section in enumerate(assessor.ok_tape_sections):
            print(f"{i}. From {section.start_position:0.2f}m to " +
                  f"{section.end_position:0.2f}m, " +
                  f"Length: {section.length:0.2f}m")


if __name__ == '__main__':
    main()
