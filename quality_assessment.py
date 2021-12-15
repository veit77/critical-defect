from typing import List, Optional
import matplotlib.pyplot as plt
from quality_data_types import QualityReport, FailInformation, FailType, TapeSpecs, TapeProduct
from tape_quality_information import TapeQualityInformation
from quality_pdf_report import DefectReportPDF


class TapeQualityAssessor():
    tape_quality_info: TapeQualityInformation
    tape_specs: TapeSpecs
    quality_reports: List[QualityReport] = []
    data_plot: Optional[plt.Figure]

    def __init__(self, tape_quality_info, tape_specs) -> None:
        self.tape_quality_info = tape_quality_info
        self.tape_specs = tape_specs

    def check_meets_specs(self):
        # prepare tape quality information
        info = self.tape_quality_info
        info.calculate_averages()
        info.calculate_basic_peak_info()
        # cl.write_peak_info("")

        self.quality_reports.append(self._check_meets_average_value())

        self.make_plot()
        self.plot_defects()

    def create_report(self):
        pass

    def print_reports(self):
        for report in self.quality_reports:
            print(f"Tape {report.tape_id} passed: {report.passed}")
            if not report.passed and report.fail_information is not None:
                for fail_info in report.fail_information:
                    print(
                        f"Failed at {fail_info.quality_parameter_info.start_position} "
                        +
                        f"to {fail_info.quality_parameter_info.end_position} "
                        +
                        f"due to: {fail_info.type.value} | {fail_info.description}"
                    )

    def _check_meets_average_value(self) -> QualityReport:
        threshold = self.tape_specs.min_average
        fails = []

        for average in self.tape_quality_info.averages:
            if average.value < threshold:
                info = FailInformation(FailType.AVERAGE, average,
                                       f"Average = {average.value}")
                fails.append(info)

        if not fails:
            return QualityReport(self.tape_quality_info.tape_id, True, None)
        else:
            return QualityReport(self.tape_quality_info.tape_id, False, fails)

    def make_plot(self):
        data = self.tape_quality_info.data
        peak_info = self.tape_quality_info.peak_info
        fig = plt.figure()
        axis = fig.subplots()
        axis.plot(data.iloc[:, 0], data.iloc[:, 1], label='Data')

        # plot fail reportss
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
                axis.plot(x,
                          y,
                          label='Fails',
                          color='r',
                          marker='|',
                          linewidth=2.0)

        peak_pos = [info.start_position for info in peak_info]
        height = [info.value for info in peak_info]
        axis.scatter(peak_pos,
                     height,
                     color='r',
                     s=15,
                     marker='D',
                     label='Maxima')
        # axis.legend()
        axis.grid()

        self.data_plot = fig

    # TODO Draw report pdf
    def save_report_pdf(self) -> None:
        pdf = DefectReportPDF(orientation="L")
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font("Times", size=12)
        for i in range(1, 41):
            pdf.cell(0, 10, f"Printing line number {i}", 0, 1)
        pdf.output("report.pdf")

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

        assessor.check_meets_specs()
        assessor.print_reports()


if __name__ == '__main__':
    main()
