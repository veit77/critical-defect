""" Class implementation for TapeQualityAssessor
"""
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from .data_types import (QualityReport, TestType, TapeSpecs, TapeSection,
                         TapeProduct)
from .helper import load_data
from .tape_quality_information import TapeQualityInformation
from .quality_pdf_report import ReportPDFCreator


class TapeQualityAssessor:
    """ Class for assessing whether specs for various quality parameters are met.
    """
    def __init__(self,
                 tape_quality_info: TapeQualityInformation,
                 tape_specs: TapeSpecs) -> None:
        self.tape_quality_info = tape_quality_info
        self.tape_specs = tape_specs
        self.quality_reports: list[QualityReport] = []
        self.ok_tape_sections: list[TapeSection] = []

    def assess_meets_specs(self) -> None:
        """ Kicks off assessment for various quality parameters and stores
            quality reports.
        """
        try:
            self.quality_reports.append(self.assess_average_value())
        except ValueError as error:
            print(f"Averages not evaluated: {repr(error)}")

        if (self.tape_specs.dropout_value is None
                or self.tape_specs.dropout_func is None):
            self.quality_reports.append(self.assess_min_value())
        else:
            self.quality_reports.append(self.assess_dropouts())

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

    def save_pdf_report(self, dirname: str = "") -> None:
        """ Creates PDF report for the tape and saves it.

        Args:
            dirname (str): directory to save the pdf to
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
        """Assesses if average value meet the specs.

        Raises:
            ValueError: In case no averages are available in Quality Info

        Returns:
            QualityReport: Quality report on average values.
        """
        if self.tape_quality_info.averages is None:
            raise ValueError("No Averages available.")
        if self.tape_specs.min_average is None:
            raise ValueError("Averages are not specified.")

        threshold = self.tape_specs.min_average
        parameter_infos = self.tape_quality_info.averages

        fails = list(filter(lambda x: x.value < threshold, parameter_infos))

        return QualityReport(self.tape_quality_info.tape_id, TestType.AVERAGE,
                             fails)

    def assess_min_value(self) -> QualityReport:
        """ Assesses if minimum values meet the specs.

        Returns:
            QualityReport: Quality report on minimum values.
        """
        threshold = self.tape_specs.min_value
        parameter_infos = self.tape_quality_info.dropouts

        fails = list(filter(lambda x: x.value < threshold, parameter_infos))

        return QualityReport(self.tape_quality_info.tape_id, TestType.MINIMUM,
                             fails)

    def assess_dropouts(self) -> QualityReport:
        """ Assesses if drop-outs meet the specs.

        Raises:
            ValueError: Exception if drop-outs are not in TapeSpecs

        Returns:
            QualityReport: Quality report on drop-outs.
        """
        if (self.tape_specs.dropout_func is None
                or self.tape_specs.dropout_value is None):
            raise ValueError("Drop-outs are not specified.")
        # A peak is a drop-out if it is smaller than min Ic
        threshold = self.tape_specs.min_value
        parameter_infos = self.tape_quality_info.dropouts
        fails = list(filter(lambda x: x.value < threshold, parameter_infos))

        # A drop-out is a fail if it is too wide or below a min Drop-out Ic
        width_func = self.tape_specs.dropout_func
        min_ic = self.tape_specs.dropout_value

        fails = list(
            filter(
                lambda x: x.value < min_ic or x.width * 1000.0 > width_func(
                    x.value), fails))

        return QualityReport(self.tape_quality_info.tape_id, TestType.DROPOUT,
                             fails)

    def plot_dropout_histogram(self) -> None:
        """ Plots Histogram of drop-out widths (Just to show what
            kind of statistics can be done).
        """
        widths = [x.width*1000 for x in self.tape_quality_info.dropouts]

        fig = plt.figure(num='Histogram')
        fig.set_tight_layout(True)
        axis = fig.subplots()
        axis.set_xlabel("Width (mm)")
        axis.set_ylabel("Count")
        axis.grid()
        axis.hist(widths, bins=60, density=True)

        fig.show()

    def _make_plot(self) -> Figure:
        data = self.tape_quality_info.data
        fig = plt.figure(num='Figure', figsize=(9.5, 3.1))
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
                elif report.test_type in [TestType.MINIMUM, TestType.DROPOUT]:
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
    """ Do all the steps to assess a tape.

    Args:
        quality_info (TapeQualityInformation): Quality information about the tape
        product (TapeSpecs): Product definition to assess the tape against
    """
    assessor = TapeQualityAssessor(quality_info, product)

    assessor.assess_meets_specs()
    assessor.plot_dropout_histogram()
    assessor.determine_ok_tape_section(product.min_tape_length)

    assessor.save_pdf_report()
    assessor.print_reports()
    assessor.plot_defects()


def main():
    """ Main function of module to test functionality of classes in module
    """
    product = TapeProduct.SUPERLINK_PHASE_TEST.value
    # expected_average = width * thickness * critical current density * factor
    # to fix units
    expected_average = product.width * 1.9 * 3 * 10
    expected_average = (product.min_average if product.min_average is not None
                        else expected_average)

    quality_info2 = [
        TapeQualityInformation(
            load_data("data/21407-3L-110_300A_Lam_Markiert.dat", False),
            "21407-3L-110", expected_average, product.average_length),
    ]

    for info in quality_info2:
        excecute_assessment(info, product)


if __name__ == '__main__':
    main()
