from typing import List, Optional
from fpdf import FPDF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
from PIL import Image
from quality_data_types import QualityReport, TapeSection


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
        self.image("./assets/THEVA-Logo.png", self.l_margin, self.t_margin, 60)
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

    def __init__(self, data_plot: Figure,
                 quality_reports: List[QualityReport],
                 ok_tape_sections: List[TapeSection],
                 tape_id: str):
        self.quality_reports = quality_reports
        self.data_plot = data_plot
        self.ok_tape_sections = ok_tape_sections
        self.tape_id = tape_id

    def create_report(self) -> None:
        """ Main function to draw content of report PDF
        """
        self._pdf = DefectReportPDF(tape_id=self.tape_id,
                                    product="product",
                                    orientation="L")
        self._pdf.alias_nb_pages()
        self._pdf.add_page()
        self._pdf.set_font("helvetica", size=11)

        # plot data graph with failure markers
        self._draw_data_plot(self._pdf.l_margin, self._pdf.t_margin + 20,
                             self._pdf.epw)

        # plot table with OK tape sections
        self._draw_ok_tape_section_list(self._pdf.l_margin,
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

    def _draw_data_plot(self, x: float, y: float, width: float):
        if self._pdf is None:
            raise ValueError("No PDF Object available")

        self._pdf.set_y(y)

        canvas = FigureCanvas(self.data_plot)
        canvas.draw()
        img = Image.fromarray(numpy.asarray(canvas.buffer_rgba()))
        self._pdf.image(img, x=x, w=width)

    def _draw_ok_tape_section_list(self, x: float, y: float):
        if self._pdf is None:
            raise ValueError("No PDF Object available")

        self._pdf.set_xy(x, y)
        line_height = self._pdf.font_size * 2.0
        self._pdf.cell(0, line_height, "**OK Tape Sections:**",
                       ln=1, markdown=True)

        # Draw table header
        self._draw_table_cells([(15, "**Nr.**", "L"),
                                (35, "**Start Position**", "L"),
                                (35, "**Start Position**", "L"),
                                (35, "**Length**", "L")],
                               line_height)

        # Draw table rows
        for i, row in enumerate(self.ok_tape_sections):
            # TODO unclear why text is bold here
            self._draw_table_cells([(15, f"{i+1}", "L"),
                                    (35, f"{row.start_position:0.2f}m", "R"),
                                    (35, f"{row.end_position:0.2f}m", "R"),
                                    (35, f"{row.length:0.2f}m", "R")],
                                   line_height)

    def _draw_table_cells(self, cell_entries: List[tuple[float, str, str]],
                          line_height: float):
        if self._pdf is None:
            raise ValueError("No PDF Object available")

        length = len(cell_entries) - 1
        for (width, entry, align) in cell_entries:
            self._pdf.multi_cell(width, line_height, entry,
                                 border=1, ln=length, align=align,
                                 max_line_height=self._pdf.font_size,
                                 markdown=True)
        self._pdf.ln(line_height)


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
