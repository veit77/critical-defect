from typing import List
from fpdf import FPDF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
from PIL import Image
from quality_data_types import QualityReport


class ReportPDFCreator():
    """ Class to create report PDF
    """
    def __init__(self, data_plot: Figure,
                 quality_reports: List[QualityReport]):
        self.quality_reports = quality_reports
        self.data_plot = data_plot

    def create_report(self) ->  None:
        """ Main function to draw content of report PDF
        """
        pdf = DefectReportPDF(orientation="L")
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font("Times", size=12)

        # plot data graph with failure markers
        canvas = FigureCanvas(self.data_plot)
        canvas.draw()
        img = Image.fromarray(numpy.asarray(canvas.buffer_rgba()))
        pdf.image(img, x=pdf.l_margin, w=pdf.epw)

        # TODO split creation from saving
        pdf.output("tuto2.pdf")


class DefectReportPDF(FPDF):
    """ Subclass of FPDF to set up page structure
    """
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
        self.cell(self.epw, 10, "Tape Quality Report", 1, 0, "C")
        # Performing a line break:
        self.ln(20)

    def footer(self):
        """ Draw footer
        """
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def main():
    """ Main function to test PDF rendering
    """
    pdf = DefectReportPDF(orientation="L")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    for i in range(1, 41):
        pdf.cell(0, 10, f"Printing line number {i}", 0, 1)
    pdf.output("tuto2.pdf")


if __name__ == "__main__":
    main()
