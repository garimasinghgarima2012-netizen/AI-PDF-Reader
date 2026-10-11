import os
import sys

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_community.vectorstores import FAISS
from embeddings import get_embedding_model

DB_DIR = "faiss_db"

def inspect_database():
    print("=" * 60)
    print(" FAISS VECTOR DATABASE INSPECTOR")
    print("=" * 60)
    
    if not os.path.exists(os.path.join(DB_DIR, "index.faiss")):
        print(f"[!] No database found at '{DB_DIR}/'.")
        print("[-] Upload and process a PDF in the app first to populate the database.")
        return

    print(f"Database Location: {os.path.abspath(DB_DIR)}")
    faiss_size = os.path.getsize(os.path.join(DB_DIR, "index.faiss")) / 1024
    pkl_size = os.path.getsize(os.path.join(DB_DIR, "index.pkl")) / 1024
    print(f"Storage Files: index.faiss ({faiss_size:.1f} KB), index.pkl ({pkl_size:.1f} KB)")
    
    print("\nLoading index into memory...")
    embedding_model = get_embedding_model()
    vs = FAISS.load_local(DB_DIR, embedding_model, allow_dangerous_deserialization=True)
    
    print(f"Total Vectors: {vs.index.ntotal}")
    print(f"Vector Dimensions: {vs.index.d} (all-MiniLM-L6-v2)")
    
    # Inspect docstore documents
    docs_dict = vs.docstore._dict
    print(f"Stored Document Chunks: {len(docs_dict)}")
    print("-" * 60)
    print("Sample Stored Chunks in Database:")
    print("-" * 60)
    for i, (doc_id, doc) in enumerate(list(docs_dict.items())[:3]):
        page = doc.metadata.get("page", "Unknown")
        snippet = doc.page_content.strip().replace("\n", " ")[:120]
        print(f"[{i+1}] ID: {doc_id[:8]}... | Page: {page}")
        print(f"    Excerpt: \"{snippet}...\"\n")
    print("=" * 60)

if __name__ == "__main__":
    inspect_database()
