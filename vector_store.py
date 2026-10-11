from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os

DB_DIR = "faiss_db"


def create_vector_store(embedding_model, documents=None, save_dir=DB_DIR):
    """
    Creates a FAISS vector store. If documents are provided, initializes
    with them and saves to disk; otherwise creates an empty store placeholder.
    """
    if documents and len(documents) > 0:
        vs = FAISS.from_documents(documents, embedding_model)
        try:
            os.makedirs(save_dir, exist_ok=True)
            vs.save_local(save_dir)
        except Exception:
            pass
        return vs

    placeholder_doc = [Document(page_content="init", metadata={})]
    return FAISS.from_documents(placeholder_doc, embedding_model)


def store_documents(documents, embedding_model, save_dir=DB_DIR):
    """
    Creates and returns a new FAISS vector store populated with documents,
    persisting the index to the local faiss_db/ folder for inspection.
    """
    if not documents:
        raise ValueError("Cannot create vector store from empty documents list.")
    
    vector_store = FAISS.from_documents(documents, embedding_model)
    try:
        os.makedirs(save_dir, exist_ok=True)
        vector_store.save_local(save_dir)
    except Exception as e:
        print(f"Warning: could not save vector store locally: {e}")
    
    return vector_store


def load_vector_store(embedding_model, save_dir=DB_DIR):
    """
    Loads an existing FAISS vector store from local disk if available.
    """
    if os.path.exists(os.path.join(save_dir, "index.faiss")):
        return FAISS.load_local(save_dir, embedding_model, allow_dangerous_deserialization=True)
    return None


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

    return store_documents(docs, emb)