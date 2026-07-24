from pypdf import PdfReader


def load_pdf(pdf_path):

    pdf_reader = PdfReader(pdf_path)

    raw_text = ""

    for page in pdf_reader.pages:
        content = page.extract_text()

        if content:
            raw_text += content

    return raw_text