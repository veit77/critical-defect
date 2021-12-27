""" Class implementation for TapeQualityAssessor
"""

from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame, read_csv
from quality_data_types import (QualityReport, TestType, TapeSpecs, TapeSection,
                                TapeProduct, QualityParameterInfo, Threshold)
from tape_quality_information import TapeQualityInformation
from quality_pdf_report import ReportPDFCreator


class TapeQualityAssessor():
    """ Class for assessing whether specs for various quality parameters are met.
    """
    tape_quality_info: TapeQualityInformation
    tape_specs: TapeSpecs
    quality_reports: List[QualityReport] = []
    ok_tape_sections: List[TapeSection] = []

    def __init__(self, tape_quality_info: TapeQualityInformation,
                 tape_specs: TapeSpecs) -> None:
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
        self.quality_reports.append(self.assess_drop_outs())

    def determine_ok_tape_section(self, min_length: float) -> None:
        """ Determines all tape section that do not contain defects and are long enough

        Args:
            min_length (float): Minimum length a defect-free tape section must be
        """
        tape_sections = [self.tape_quality_info.tape_section]

        for q_report in self.quality_reports:
            if q_report.fail_information is None:
                continue
            for fail_info in q_report.fail_information:
                # find all sections that overlap with the current defect
                sections_to_devide = [
                    section for section in tape_sections
                    if (fail_info.start_position > section.start_position
                        and fail_info.start_position < section.end_position) or
                    (fail_info.end_position > section.start_position
                     and fail_info.end_position < section.end_position)
                ]
                for section in sections_to_devide:
                    # remove section, then cut defective part from section and
                    # append it again
                    tape_sections.remove(section)
                    if fail_info.end_position > section.end_position:
                        tape_sections.append(
                            TapeSection(section.start_position,
                                        fail_info.start_position))
                    elif fail_info.start_position < section.start_position:
                        tape_sections.append(
                            TapeSection(fail_info.end_position,
                                        section.end_position))
                    else:
                        tape_sections.append(
                            TapeSection(section.start_position,
                                        fail_info.start_position))
                        tape_sections.append(
                            TapeSection(fail_info.end_position,
                                        section.end_position))

        tape_sections = [
            tape_sec for tape_sec in tape_sections
            if tape_sec.length >= min_length
        ]

        self.ok_tape_sections = tape_sections

    def save_pdf_report(self) -> None:
        """ Creates PDF report for the tape and saves it.
        """
        pdf_report = ReportPDFCreator(self.tape_quality_info.tape_id,
                                      self.tape_specs.description,
                                      self._make_plot(),
                                      self.quality_reports,
                                      self.ok_tape_sections)
        pdf_report.create_report()
        pdf_report.save_report(f"Report {self.tape_quality_info.tape_id}.pdf")

    def plot_defects(self) -> None:
        """ Shows plot in a window.
        """
        _ = self._make_plot()

        plt.show()

    def print_reports(self):
        """ print all available quality reports to the shell.
        """
        for report in self.quality_reports:
            print(f"Tape {report.tape_id} passed: {report.passed}")
            if not report.passed and report.fail_information is not None:
                if report.test_type is not None:
                    print(f"Failed due to: {report.test_type.value}")
                else:
                    print("Failed for unknown reason")
                for fail_info in report.fail_information:
                    print(fail_info.description)

    def assess_average_value(self) -> QualityReport:
        """ Assesses if average value meet the specs.

        Returns:
            QualityReport: Quality report on average values.
        """
        threshold = Threshold(value=self.tape_specs.min_average)
        return self._assess_failure(TestType.AVERAGE,
                                    threshold,
                                    self.tape_quality_info.averages)

    def assess_min_value(self) -> QualityReport:
        """ Assesses if minimum values meet the specs.

        Returns:
            QualityReport: Quality report on minimum values.
        """
        threshold = Threshold(value=self.tape_specs.min_value)
        return self._assess_failure(TestType.MINIMUM,
                                    threshold,
                                    self.tape_quality_info.drop_outs)

    def assess_drop_outs(self) -> QualityReport:
        """ Assesses if drop-outs meet the specs.

        Returns:
            QualityReport: Quality report on drop-outs.
        """
        # TODO Drop-outs if allowed can rehabilitate min_value failures
        threshold = Threshold(width=self.tape_specs.drop_out_width,
                              value=self.tape_specs.drop_out_value)
        return self._assess_failure(TestType.DROP_OUT, threshold,
                                    self.tape_quality_info.drop_outs)

    def _assess_failure(
            self, test_type: TestType, threshold: Threshold,
            parameter_infos: List[QualityParameterInfo]) -> QualityReport:
        """ Assesses if selected quality parameter meets the specs.

        Args:
            test_type (TestType): Qualityparameter to assess.
            threshold (Threshold): Threshold to pass specs.
            parameter_infos (List[QualityParameterInfo])

        Returns:
            QualityReport: Quality report on selected quality parameter.
        """
        # TODO This only implements the "all" Option in Threshold
        fails = parameter_infos
        if threshold.width is not None:
            fails = [p_info for p_info in parameter_infos
                     if p_info.width > threshold.width]
        if threshold.value is not None:
            fails = [p_info for p_info in parameter_infos
                     if p_info.value < threshold.value]

        if not fails:
            return QualityReport(self.tape_quality_info.tape_id, test_type,
                                 True)
        else:
            return QualityReport(self.tape_quality_info.tape_id, test_type,
                                 False, fails)

    def _make_plot(self) -> Figure:
        data = self.tape_quality_info.data
        fig = plt.figure(num='figure', figsize=(9.5, 3.1))
        fig.set_tight_layout(True)
        axis = fig.subplots()
        axis.set_xlabel("Position (m)")
        axis.set_ylabel("Critical Current (A)")
        axis.grid()
        axis.plot(data.iloc[:, 0], data.iloc[:, 1], label='Data')

        # plot fail reports
        for report in self.quality_reports:
            if report.fail_information is None:
                continue
            for fail in report.fail_information:
                x = [fail.start_position,
                     fail.end_position]
                y = [fail.value,
                     fail.value]

                if report.test_type == TestType.AVERAGE:
                    color = 'crimson'
                    axis.plot(x, y,
                              color=color,
                              marker='|',
                              linewidth=2.0,
                              label='Averages Failed')
                elif report.test_type in [TestType.MINIMUM, TestType.DROP_OUT]:
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

        return fig


def excecute_assessment(quality_info: TapeQualityInformation,
                        product: TapeSpecs) -> None:
    assessor = TapeQualityAssessor(quality_info, product)

    assessor.assess_meets_specs()
    assessor.determine_ok_tape_section(product.min_tape_length)

    assessor.save_pdf_report()
    assessor.print_reports()
    assessor.plot_defects()


def main():
    """ Main function of module to test functionality of classes in module
    """
    from multiprocessing import Pool
    from functools import partial

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

    with Pool() as pool:
        pool.map(partial(excecute_assessment, product=product), quality_info)

    # for q_info in quality_info:
    #     assessor = TapeQualityAssessor(q_info, product)

    #     assessor.assess_meets_specs()
    #     assessor.determine_ok_tape_section(product.min_tape_length)

    #     assessor.save_pdf_report()
    #     assessor.print_reports()
    #     assessor.plot_defects()


if __name__ == '__main__':
    main()
