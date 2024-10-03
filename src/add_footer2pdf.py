from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
import io
import pathlib as pl
from reportlab.pdfgen import canvas

# Todo: Add futura as a font for the footer
# from reportlab.pdfbase import ttfonts, pdfmetrics
# pdfmetrics.registerFont(ttfonts.TTFont("Futura", "SomeFontFile.ttf"))

# Width: 612 points (8.5 inches * 72 points per inch)
# Height: 792 points (11 inches * 72 points per inch)


def create_footer_pdf(
    num_pages: int,
    footer_text="AISF Readings — Page {i} of {n}",
    font_name="Helvetica",
    font_size=8,
    skip_pages=[1, 2],
) -> PdfReader:
    assert isinstance(num_pages, int)
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont(font_name, font_size)

    for i in range(num_pages):
        if i not in list(map(lambda j: j - 1, skip_pages)):
            footer = footer_text.format(i=i + 1, n=num_pages)
            footer_width = c.stringWidth(footer, font_name, font_size)
            footer_object = c.beginText((letter[0] - footer_width) / 2, 20)
            footer_object.setFont(font_name, font_size)
            footer_object.textOut(footer)
            c.drawText(footer_object)
        c.showPage()
    c.save()
    packet.seek(0)
    return PdfReader(packet)


def add_footer_to_pdf(
    input_pdf_path: pl.Path,
    output_pdf_path: pl.Path,
    footer_text: str = "AISF Readings — Page {i} of {n}",
) -> pl.Path:
    assert isinstance(input_pdf_path, pl.Path)
    assert isinstance(output_pdf_path, pl.Path)

    # Create footer pdf
    pdf_reader = PdfReader(open(str(input_pdf_path), "rb"))
    num_pages = len(pdf_reader.pages)
    footer_pdf = create_footer_pdf(num_pages, footer_text=footer_text)

    # Create a PdfWriter object
    pdf_writer = PdfWriter()
    # Add pages with footer to PdfWriter
    for i in range(num_pages):
        page = pdf_reader.pages[i]
        footer_page = footer_pdf.pages[i]
        page.merge_page(footer_page)
        pdf_writer.add_page(page)

    # Write the pages to a new PDF file
    with open(str(output_pdf_path), "wb") as f_out:
        pdf_writer.write(f_out)

    return output_pdf_path


if __name__ == "__main__":
    input_pdf_path = pl.Path("output/test1/aisf_ml_meeting_5__model_internals.pdf")
    output_pdf_path = pl.Path(
        "output/test1/FOOTER aisf_ml_meeting_5__model_internals.pdf"
    )
    add_footer_to_pdf(input_pdf_path, output_pdf_path)
