from fpdf import FPDF
from tape_quality_information import TapeQualityInformation


class ReportPDFCreator():
    def __init__(self, quality_info: TapeQualityInformation):
        self.quality_info = quality_info

    def create_report(self):
        pdf = DefectReportPDF(orientation="L")
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font("Times", size=12)
        for i in range(1, 41):
            pdf.cell(0, 10, f"Printing line number {i}", 0, 1)
        pdf.output("tuto2.pdf")


class DefectReportPDF(FPDF):
    def header(self):
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
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def main():
    pdf = DefectReportPDF(orientation="L")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    for i in range(1, 41):
        pdf.cell(0, 10, f"Printing line number {i}", 0, 1)
    pdf.output("tuto2.pdf")


if __name__ == "__main__":
    main()
