import pymupdf 
from IPython.display import display, Image, HTML
from pathlib import Path


def preview_pdf(pdf_path, dpi=150):
    pdf_path = Path(pdf_path)

    display(HTML(
    f"""<div style='border:1px solid #d9e2e6;border-radius:8px;overflow:hidden;background:white'>
    <object data='data:application/pdf;base64,{pdf_path}' type='application/pdf' width='100%' height='680px'>
      <div style='padding:18px'>PDF can also be opened in a new tab:
      <a href='{pdf_path.as_posix()}' target='_blank'>Open DF323.pdf</a>.</div>
    </object></div>"""
    ))

    doc = pymupdf.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        display(Image(pix.tobytes("png")))
    doc.close()
