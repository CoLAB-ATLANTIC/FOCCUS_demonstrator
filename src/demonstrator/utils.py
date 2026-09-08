import pymupdf 
from IPython.display import display, Image, HTML,FileLink
from pathlib import Path

def preview_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    display(FileLink(pdf_path, result_html_prefix="PDF image can be opened in a separate tab using this link: "))

    # Render pages as images
    doc = pymupdf.open(pdf_path)

    for page in doc:
        pix = page.get_pixmap(dpi=150)
        display(Image(pix.tobytes("png")))

    doc.close()
