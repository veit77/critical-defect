from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame, read_csv
from quality_data_types import QualityReport, FailInformation, FailType, TapeSpecs, TapeProduct, QualityParameterInfo
from tape_quality_information import TapeQualityInformation
from quality_pdf_report import ReportPDFCreator


class TapeQualityAssessor():
    tape_quality_info: TapeQualityInformation
    tape_specs: TapeSpecs
    quality_reports: List[QualityReport] = []

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
            convert_to_meters (bool, optional): Convert postions from mm to meters. Defaults to False.

        Returns:
            DataFrame: Ic-data from TapeStar csv-file
        """
        data = read_csv(from_path, header=1, delimiter="\t")

        if convert_to_meters:
            data.iloc[:, 0] = data.iloc[:, 0].div(1000.0)
        return data

    def assess_meets_specs(self):
        # assess different spec categories
        self.quality_reports.append(self.assess_average_value())
        self.quality_reports.append(self.assess_min_value())

    def save_pdf_report(self) -> None:
        pdf_report = ReportPDFCreator(self._make_plot(), self.quality_reports)
        pdf_report.create_report()
        # TODO add saving

    def plot_defects(self) -> None:
        _ = self._make_plot()

        plt.show()

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
                        + f"with: {fail_info.description}")

    def assess_average_value(self) -> QualityReport:
        return self._assess_failure(FailType.AVERAGE)

    def assess_min_value(self) -> QualityReport:
        return self._assess_failure(FailType.MINIMUM)

    def _assess_failure(self, fail_type: FailType) -> QualityReport:
        threshold = 0
        parameter_infos: List[QualityParameterInfo] = []
        parameter_string = ""
        if fail_type == FailType.AVERAGE:
            threshold = self.tape_specs.min_average
            parameter_infos = self.tape_quality_info.averages
            parameter_string = "Average"
        elif fail_type == FailType.MINIMUM:
            threshold = self.tape_specs.min_value
            parameter_infos = self.tape_quality_info.drop_outs
            parameter_string = "Peak"

        fails = []

        for p_info in parameter_infos:
            if p_info.value < threshold:
                info = FailInformation(p_info,
                                       f"{parameter_string} = {p_info.value}")
                fails.append(info)

        if not fails:
            return QualityReport(self.tape_quality_info.tape_id, True)
        else:
            return QualityReport(self.tape_quality_info.tape_id, False, fail_type,
                                 fails)

    def _make_plot(self) -> Figure:
        data = self.tape_quality_info.data
        fig = plt.figure(figsize=(9.5, 3.1))
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
                    axis.plot(x,
                              y,
                              color=color,
                              marker='|',
                              linewidth=2.0,
                              label='Averages Failed')
                elif report.type == FailType.MINIMUM:
                    color = 'deeppink'
                    axis.scatter(x,
                                 y,
                                 color=color,
                                 s=15,
                                 marker='D',
                                 label='Minimum Failed')

        # axis.legend()
        plt.xlabel("Position (m)")
        plt.ylabel("Critical Current (A)")
        axis.grid()

        return fig


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

        assessor.save_pdf_report()
        assessor.print_reports()
        assessor.plot_defects()


if __name__ == '__main__':
    main()
