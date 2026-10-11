import os
import tempfile
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

import importlib
import config
import loader
import text_splitter
import embeddings
import vector_store
import retriever
import llm
import rag

# Ensure modules are freshly reloaded from disk in the correct dependency order
for mod in [config, loader, text_splitter, embeddings, vector_store, retriever, llm, rag]:
    try:
        importlib.reload(mod)
    except Exception:
        pass

from loader import load_pdf
from text_splitter import split_documents
from embeddings import get_embedding_model
from vector_store import store_documents
from retriever import get_retriever
from llm import get_llm
from rag import create_rag_pipeline


# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="DocuMind AI | PDF Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS STYLING ----------------
st.markdown("""
<style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.5rem;
    }

    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .brand-tagline {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }

    .badge-pill.db {
        background: rgba(52, 211, 153, 0.12);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.25);
    }

    .badge-pill.llm {
        background: rgba(192, 132, 252, 0.12);
        color: #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.25);
    }

    /* Cards */
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #334155;
        text-align: center;
    }
    .metric-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .source-badge {
        display: inline-block;
        background: #1e293b;
        color: #38bdf8;
        border: 1px solid #38bdf8;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 6px;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE SETUP ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = None

if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "processed_hash" not in st.session_state:
    st.session_state.processed_hash = None


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📂 Document Control")
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload any PDF to parse, embed, and query with AI."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")

    selected_model = st.selectbox(
        "LLM Model (Groq)",
        options=["openai/gpt-oss-20b", "qwen/qwen3.8-27b"],
        index=0,
        help="Ultra-fast open models hosted on Groq LPU inference."
    )

    top_k = st.slider(
        "Retrieval Top-K Chunks",
        min_value=2,
        max_value=8,
        value=4,
        step=1,
        help="Number of most relevant passages sent to the model."
    )

    view_mode = st.radio(
        "Interface Mode",
        options=["Split View (PDF + Chat)", "Full Screen Chat"],
        index=0
    )

    # Process Document Button
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hash(file_bytes)

        if st.session_state.processed_hash != file_hash:
            if st.button("🚀 Process & Index PDF", use_container_width=True, type="primary"):
                with st.status("Analyzing document and creating vector index...", expanded=True) as status:
                    # 1. Save to temp file
                    status.write("📄 Reading PDF pages...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(file_bytes)
                        tmp_file_path = tmp_file.name

                    try:
                        # 2. Extract Document pages
                        raw_docs = load_pdf(tmp_file_path)
                        total_pages = len(raw_docs)
                        status.write(f"✅ Extracted {total_pages} pages successfully.")

                        # 3. Split into chunks preserving metadata
                        status.write("✂️ Splitting content into semantically overlapping passages...")
                        chunks = split_documents(raw_docs, chunk_size=1000, chunk_overlap=150)
                        status.write(f"✅ Created {len(chunks)} contextual chunks with page metadata.")

                        # 4. Embeddings & FAISS Vector Store
                        status.write("🧠 Generating embeddings with MiniLM & building FAISS index...")
                        embedding_model = get_embedding_model()
                        vector_store = store_documents(chunks, embedding_model)
                        status.write("✅ High-performance FAISS Vector Database ready.")

                        # 5. Build RAG pipeline
                        status.write("🤖 Connecting Groq LLM & RAG pipeline...")
                        retriever = get_retriever(vector_store, k=top_k)
                        llm = get_llm(model_name=selected_model)
                        st.session_state.rag = create_rag_pipeline(retriever, llm)

                        # Save state
                        st.session_state.pdf_bytes = file_bytes
                        st.session_state.processed_hash = file_hash
                        st.session_state.indexed_chunks = chunks
                        st.session_state.doc_stats = {
                            "filename": uploaded_file.name,
                            "pages": total_pages,
                            "chunks": len(chunks),
                            "size_kb": round(len(file_bytes) / 1024, 1),
                        }
                        status.update(label="🎉 PDF Indexed and Ready for Chat!", state="complete", expanded=False)
                        st.rerun()

                    except Exception as err:
                        status.update(label=f"❌ Error: {str(err)}", state="error")
                        st.error(f"Failed to process document: {err}")
                    finally:
                        if os.path.exists(tmp_file_path):
                            try:
                                os.remove(tmp_file_path)
                            except Exception:
                                pass

    # Display Document Stats if indexed
    if st.session_state.doc_stats:
        st.markdown("---")
        st.markdown("### 📊 Document Overview")
        st.caption(f"📁 **{st.session_state.doc_stats['filename']}**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{st.session_state.doc_stats['pages']}</div>
                <div class="metric-label">Pages</div>
            </div>
            """, unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{st.session_state.doc_stats['chunks']}</div>
                <div class="metric-label">Chunks</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("🗄️ Database Inspector", expanded=False):
            st.markdown("**Status:** `🟢 Connected & Active`")
            st.markdown("**Engine:** `FAISS (IndexFlatL2)`")
            st.markdown("**Storage Folder:** `C:\\pdf_query\\faiss_db\\`")
            st.markdown(f"**Stored Vectors:** `{st.session_state.doc_stats['chunks']}`")
            st.markdown("**Dimensions:** `384` (MiniLM-L6)")
            st.code("Files on disk:\n- faiss_db/index.faiss (Vectors)\n- faiss_db/index.pkl (Docstore)")

            if "indexed_chunks" in st.session_state and st.session_state.indexed_chunks:
                st.markdown("---")
                st.markdown("**Sample Stored Chunks:**")
                for idx, c in enumerate(st.session_state.indexed_chunks[:3]):
                    p_num = c.metadata.get("page", 1)
                    st.caption(f"**Chunk #{idx+1} (Page {p_num}):**")
                    st.text(c.page_content.strip()[:140] + "...")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


# ---------------- MAIN HEADER ----------------
st.markdown("""
<div class="main-header">
    <div>
        <h1 class="brand-title">🧠 DocuMind AI</h1>
        <div class="brand-tagline">Advanced Neural PDF Search & Conversational RAG</div>
    </div>
    <div>
        <span class="badge-pill db">⚡ FAISS Vector DB</span>
        <span class="badge-pill llm">⚡ Groq LPU</span>
        <span class="badge-pill">MiniLM-L6</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- CHAT / VIEW LAYOUT ----------------
def render_chat_container():
    # If no messages, render welcome and quick prompt buttons
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
            <h3 style="margin-top: 0;">👋 Welcome to DocuMind AI</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">
                Upload a document in the sidebar to start asking questions with instant page-referenced citations.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.rag is not None:
            st.markdown("**💡 Quick Questions:**")
            quick_cols = st.columns(3)
            with quick_cols[0]:
                if st.button("📋 Summarize key points", use_container_width=True):
                    st.session_state["pending_prompt"] = "Please provide an executive summary and key points of this document."
                    st.rerun()
            with quick_cols[1]:
                if st.button("🔍 Explain main methodology", use_container_width=True):
                    st.session_state["pending_prompt"] = "What are the core concepts and methodologies discussed?"
                    st.rerun()
            with quick_cols[2]:
                if st.button("📌 List conclusions & takeaways", use_container_width=True):
                    st.session_state["pending_prompt"] = "What are the main conclusions, findings, or action items?"
                    st.rerun()

    # Display past conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🧠"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                badges_html = " ".join([f"<span class='source-badge'>📄 Page {p}</span>" for p in msg["sources"]])
                st.markdown(f"<div style='margin-top: 8px;'>{badges_html}</div>", unsafe_allow_html=True)
            
            # Show retrieved snippets accordion if present
            if msg.get("docs"):
                with st.expander("🔍 View Retrieved Passages"):
                    for i, doc in enumerate(msg["docs"]):
                        page_num = doc.metadata.get("page", "Unknown")
                        st.markdown(f"**Passage {i+1} (Page {page_num}):**")
                        st.caption(doc.page_content.strip())


# Render Layout based on user preference
if view_mode == "Split View (PDF + Chat)" and st.session_state.pdf_bytes:
    col_pdf, col_chat = st.columns([1, 1], gap="medium")
    with col_pdf:
        st.subheader("📑 Document Viewer")
        pdf_viewer(input=st.session_state.pdf_bytes, height=750)
    with col_chat:
        st.subheader("💬 AI Conversation")
        render_chat_container()
else:
    render_chat_container()


# ---------------- PROMPT HANDLING ----------------
pending = st.session_state.pop("pending_prompt", None)
user_query = st.chat_input("Ask a question about your document...")

prompt_to_run = user_query or pending

if prompt_to_run:
    if st.session_state.rag is None:
        st.warning("⚠️ Please upload and process a PDF in the sidebar first.")
    else:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt_to_run
        })

        with st.spinner("Analyzing document context..."):
            try:
                result = st.session_state.rag(
                    prompt_to_run,
                    chat_history=st.session_state.messages[:-1]
                )
                answer = result.get("answer", "No answer could be generated.")
                sources = result.get("sources", [])
                docs = result.get("docs", [])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "docs": docs
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ An error occurred while retrieving answer: {str(e)}",
                    "sources": [],
                    "docs": []
                })

        st.rerun()