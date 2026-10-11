from pypdf import PdfReader
from langchain_core.documents import Document


def load_pdf(pdf_path: str):
    """
    Reads a PDF file page by page and returns a list of Document objects
    retaining page numbers in their metadata for precise source citation.
    """
    reader = PdfReader(pdf_path)
    documents = []
    total_pages = len(reader.pages)

    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": idx + 1,
                        "source": pdf_path,
                        "total_pages": total_pages,
                    },
                )
            )

    return documents