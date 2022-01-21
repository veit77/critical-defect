""" Class implementation for DefectReportPDF
"""
from typing import List, Optional
from os import path
from fpdf import FPDF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
from PIL import Image
from .data_types import QualityReport, TapeSection


class DefectReportPDF(FPDF):
    """ Subclass of FPDF to set up page structure
    """
    def __init__(self, tape_id: str, product: str, orientation: str):
        self.tape_id = tape_id
        self.product = product
        super().__init__(orientation=orientation)

    def header(self):
        """ Draw header
        """
        # Rendering logo:
        logo_path = path.join(path.dirname(__file__), 'assets/THEVA-Logo.png')
        self.image(logo_path, self.l_margin, self.t_margin, 60)
        # Setting font: helvetica bold 15
        self.set_font("helvetica", "B", 20)
        # Moving cursor to the right:
        self.set_x(self.l_margin)
        # Printing title:
        self.cell(self.epw, 10, "Tape Quality Report", 0, 0, "C")

        self.set_x(self.epw)
        # Printing title:
        self.set_font("helvetica", size=11)
        self.cell(0, self.font_size,
                  f"**Tape ID:** {self.tape_id}",
                  0, 1, "R", markdown=True)
        self.cell(0, self.font_size,
                  f"**Product:** {self.product}",
                  0, 1, "R", markdown=True)

    def footer(self):
        """ Draw footer
        """
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


class ReportPDFCreator():
    """ Class to create report PDF
    """
    _pdf: Optional[DefectReportPDF] = None

    def __init__(self, tape_id: str, product: str,
                 data_plot: Figure,
                 quality_reports: List[QualityReport],
                 ok_tape_sections: List[TapeSection]):

        self.tape_id = tape_id
        self.product = product
        self.data_plot = data_plot
        self.quality_reports = quality_reports
        self.ok_tape_sections = ok_tape_sections

    def create_report(self) -> None:
        """ Main function to draw content of report PDF
        """
        self._pdf = DefectReportPDF(tape_id=self.tape_id,
                                    product=self.product,
                                    orientation="L")
        self._pdf.alias_nb_pages()
        self._pdf.add_page()
        self._pdf.set_font("helvetica", size=11)

        # plot data graph with failure markers
        self._draw_data_plot(self._pdf, self._pdf.l_margin,
                             self._pdf.t_margin + 20, self._pdf.epw)

        # plot table with OK tape sections
        self._draw_ok_tape_section_list(
            self._pdf, self._pdf.l_margin + self._pdf.epw / 2.0,
            self._pdf.t_margin + 110)

        # plot table with test pass informations
        self._draw_test_pass_info(self._pdf, self._pdf.l_margin,
                                  self._pdf.t_margin + 110)

    def save_report(self, to_path: str) -> None:
        """ Save the PDF to disk.

        Args:
            to_path (str): Path (incl. file name) to save the PDF to.

        Raises:
            ValueError: Raised if the PDF cannot is not created (is None).
        """
        if self._pdf is None:
            raise ValueError("PDF has not been created yet.")
        self._pdf.output(to_path)

    def _draw_data_plot(self, pdf: DefectReportPDF, x: float, y: float,
                        width: float) -> None:
        pdf.set_y(y)

        canvas = FigureCanvas(self.data_plot)
        canvas.draw()
        img = Image.fromarray(numpy.asarray(canvas.buffer_rgba()))
        pdf.image(img, x=x, w=width)

    def _draw_ok_tape_section_list(self, pdf: DefectReportPDF, x: float,
                                   y: float) -> None:
        line_height = self._draw_head_line(pdf, x, y, "**OK Tape Sections:**")

        self._draw_table_cells(pdf, [(15, "**Nr.**", "L"),
                                     (35, "**Start Position**", "L"),
                                     (35, "**Start Position**", "L"),
                                     (35, "**Length**", "L")], line_height)

        # Draw table rows
        for i, row in enumerate(self.ok_tape_sections):
            # TODO unclear why text is bold here
            pdf.set_x(x)
            self._draw_table_cells(pdf,
                                   [(15, f"{i+1}", "L"),
                                    (35, f"{row.start_position:0.2f}m", "R"),
                                    (35, f"{row.end_position:0.2f}m", "R"),
                                    (35, f"{row.length:0.2f}m", "R")],
                                   line_height)

    def _draw_test_pass_info(self, pdf: DefectReportPDF, x: float,
                             y: float) -> None:
        line_height = self._draw_head_line(pdf, x, y,
                                           "**Test Pass Information:**")

        self._draw_table_cells(pdf, [(35, "**Test**", "L"),
                                     (35, "**Pass/Fail**", "L"),
                                     (35, "**Number of Fails", "L")],
                               line_height)
        for report in self.quality_reports:
            # TODO unclear why text is bold here
            passed = "Pass" if report.passed else "Fail"
            nb_failed = ""
            if report.fail_information is not None:
                if len(report.fail_information) == 0:
                    nb_failed = ""
                else:
                    nb_failed = f"{len(report.fail_information)}"
            pdf.set_x(x)
            self._draw_table_cells(pdf,
                                   [(35, f"{report.test_type.value}", "L"),
                                    (35, passed, "C"),
                                    (35, nb_failed, "R")], line_height)

    def _draw_head_line(self, pdf: DefectReportPDF, x: float, y: float,
                        head_line: str) -> float:
        pdf.set_xy(x, y)
        result = pdf.font_size * 2.0
        pdf.cell(0, result, head_line, ln=1, markdown=True)
        pdf.set_x(x)
        return result

    def _draw_table_cells(self, pdf: DefectReportPDF,
                          cell_entries: List[tuple[float, str, str]],
                          line_height: float) -> None:
        for (width, entry, align) in cell_entries:
            pdf.multi_cell(width, line_height, entry,
                           border=1, ln=3, align=align,
                           max_line_height=pdf.font_size,
                           markdown=True)
        pdf.ln(line_height)


def main():
    """ Main function to test PDF rendering
    """
    pdf = DefectReportPDF(tape_id="tape_id", product="product", orientation="L")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    for i in range(1, 41):
        pdf.cell(0, 10, f"Printing line number {i}", 0, 1)
    pdf.output("tuto2.pdf")


if __name__ == "__main__":
    main()
