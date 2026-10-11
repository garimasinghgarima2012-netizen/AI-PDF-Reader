from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os


def create_vector_store(embedding_model, documents=None):
    """
    Creates a FAISS vector store. If documents are provided, initializes
    with them; otherwise creates an empty store placeholder.
    """
    if documents and len(documents) > 0:
        return FAISS.from_documents(documents, embedding_model)
    # Placeholder if called without documents
    placeholder_doc = [Document(page_content="init", metadata={})]
    vs = FAISS.from_documents(placeholder_doc, embedding_model)
    return vs


def store_documents(documents, embedding_model):
    """
    Creates and returns a new FAISS vector store populated with documents,
    preserving all metadata such as page numbers.
    """
    if not documents:
        raise ValueError("Cannot create vector store from empty documents list.")
    vector_store = FAISS.from_documents(documents, embedding_model)
    return vector_store


def store_chunks(vector_store, chunks, embedding_model=None):
    """
    Backwards compatibility: takes text chunks and adds them to a vector store.
    """
    if isinstance(chunks, list) and len(chunks) > 0 and isinstance(chunks[0], str):
        docs = [Document(page_content=c, metadata={}) for c in chunks]
    else:
        docs = chunks

    emb = embedding_model if embedding_model else getattr(vector_store, "embedding_function", None)
    if emb is None:
        from embeddings import get_embedding_model
        emb = get_embedding_model()

    return FAISS.from_documents(docs, emb)