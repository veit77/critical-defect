from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from quality_data_types import QualityReport, FailInformation, FailType, TapeSpecs, TapeProduct, QualityParameterInfo
from tape_quality_information import TapeQualityInformation
from quality_pdf_report import ReportPDFCreator


class TapeQualityAssessor():
    tape_quality_info: TapeQualityInformation
    tape_specs: TapeSpecs
    quality_reports: List[QualityReport] = []
    data_plot: Optional[Figure]

    def __init__(self, tape_quality_info, tape_specs) -> None:
        self.tape_quality_info = tape_quality_info
        self.tape_specs = tape_specs
        self.quality_reports = []
        self.data_plot = None

    def assess_meets_specs(self):
        # prepare tape quality information
        info = self.tape_quality_info
        info.calculate_averages()
        info.calculate_basic_peak_info()

        # assess different spec categories
        self.quality_reports.append(self.assess_average_value())
        self.quality_reports.append(self.assess_min_value())

        # make the data plot containing all failure infos
        self.make_plot()

    def create_pdf_report(self):
        if self.data_plot is None:
            raise ValueError("No data plot available.")

        pdf_report = ReportPDFCreator(self.data_plot, self.quality_reports)
        pdf_report.create_report()

    def print_reports(self):
        for report in self.quality_reports:
            print(f"Tape {report.tape_id} passed: {report.passed}")
            if not report.passed and report.fail_information is not None:
                print(f"Failed due to: {report.type.value}")
                for fail_info in report.fail_information:
                    print(
                        f"Failed at {fail_info.quality_parameter_info.start_position:.2f} "
                        +
                        f"to {fail_info.quality_parameter_info.end_position:.2f} "
                        +
                        f"with: {fail_info.description}"
                    )

    def assess_average_value(self) -> QualityReport:
        return self._assess_failure(FailType.AVERAGE)

    def assess_min_value(self) -> QualityReport:
        return self._assess_failure(FailType.MINIMUM)

    def _assess_failure(self, type: FailType) -> QualityReport:
        threshold = 0
        parameter_infos: List[QualityParameterInfo] = []
        parameter_string = ""
        if type == FailType.AVERAGE:
            threshold = self.tape_specs.min_average
            parameter_infos = self.tape_quality_info.averages
            parameter_string = "Average"
        elif type == FailType.MINIMUM:
            threshold = self.tape_specs.min_value
            parameter_infos = self.tape_quality_info.peaks
            parameter_string = "Peak"

        fails = []

        for p_info in parameter_infos:
            if p_info.value < threshold:
                info = FailInformation(p_info, f"{parameter_string} = {p_info.value}")
                fails.append(info)

        if not fails:
            return QualityReport(self.tape_quality_info.tape_id, True)
        else:
            return QualityReport(self.tape_quality_info.tape_id, False, type, fails)

    def make_plot(self):
        data = self.tape_quality_info.data
        fig = plt.figure()
        axis = fig.subplots()
        axis.plot(data.iloc[:, 0], data.iloc[:, 1], label='Data')

        # plot fail reports
        # TODO evaluate for fail type -> color of marker
        for report in self.quality_reports:
            if report.fail_information is None:
                continue
            for fail in report.fail_information:
                x = [
                    fail.quality_parameter_info.start_position,
                    fail.quality_parameter_info.end_position
                ]
                y = [
                    fail.quality_parameter_info.value,
                    fail.quality_parameter_info.value
                ]

                if report.type == FailType.AVERAGE:
                    color = 'crimson'
                    axis.plot(x, y, color=color,
                              marker='|',
                              linewidth=2.0,
                              label='Averages Failed')
                elif report.type == FailType.MINIMUM:
                    color = 'deeppink'
                    axis.scatter(x, y, color=color,
                                 s=15,
                                 marker='D',
                                 label='Minimum Failed')

        # axis.legend()
        axis.grid()

        self.data_plot = fig

    # TODO Draw report pdf
    def save_report_pdf(self) -> None:
        pdf = ReportPDFCreator(self.data_plot, self.quality_reports)
        pdf.create_report()

    def plot_defects(self):
        if self.data_plot is None:
            raise ValueError("No Data available.")

        _ = self.data_plot

        plt.show()


def main():
    product = TapeProduct.STANDARD.value
    quality_info = [
        TapeQualityInformation(
            TapeQualityInformation.load_data("data/20204-X-10_500A.dat",
                                             False), "20204-X-10",
            product.min_average, product.average_length),
        TapeQualityInformation(
            TapeQualityInformation.load_data(
                "data/17346-X-11-BL_30_29970_500A.dat", True), "17346-X-11",
            product.min_average, product.average_length)
    ]

    for q_info in quality_info:
        assessor = TapeQualityAssessor(q_info, TapeProduct.STANDARD.value)
        assessor.tape_quality_info = q_info

        assessor.assess_meets_specs()

        assessor.create_pdf_report()
        assessor.print_reports()


if __name__ == '__main__':
    main()
