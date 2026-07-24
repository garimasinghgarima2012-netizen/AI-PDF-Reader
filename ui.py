import streamlit as st

from loader import load_pdf
from text_splitter import split_text
from embeddings import get_embedding_model
from vector_store import create_vector_store, store_chunks
from rag import create_rag_pipeline
from llm import get_llm



# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide"
)



# ---------------- DARK UI CSS ----------------

st.markdown(
    """
    <style>

    /* Main background */

    .stApp {

        background-color:#0f172a;

        color:white;

    }


    /* Sidebar */

    section[data-testid="stSidebar"] {

        background-color:#020617;

    }



    /* Title */

    .title {

        font-size:48px;

        font-weight:800;

        background:
        linear-gradient(
        90deg,
        #38bdf8,
        #818cf8
        );

        -webkit-background-clip:text;

        color:transparent;

    }



    .subtitle {

        color:#94a3b8;

        font-size:18px;

    }



    /* Cards */

    .card {

        background:#111827;

        padding:25px;

        border-radius:18px;

        border:1px solid #1e293b;

        box-shadow:
        0 10px 30px rgba(0,0,0,0.4);

    }



    /* Buttons */

    .stButton button {


        background:
        linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
        );


        color:white;

        border:none;

        border-radius:12px;

        height:45px;

        font-weight:600;

        width:100%;


    }



    .stButton button:hover {

        opacity:0.85;

    }



    /* Chat input */


    .stChatInput input {

        background:#111827;

        color:white;

        border-radius:20px;

    }



    /* Text */

    p, h1, h2, h3 {

        color:white;

    }


    </style>

    """,

    unsafe_allow_html=True
)





# ---------------- SESSION ----------------


if "rag" not in st.session_state:

    st.session_state.rag=None



if "messages" not in st.session_state:

    st.session_state.messages=[]





# ---------------- HEADER ----------------


st.markdown(
    "<div class='title'>🧠 DocuMind AI</div>",
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class='subtitle'>

    Chat with your PDF using Retrieval Augmented Generation

    </div>
    """,

    unsafe_allow_html=True
)



st.write("")



# ---------------- SIDEBAR ----------------


with st.sidebar:


    st.markdown(
        "## 📂 Upload Document"
    )


    uploaded_file = st.file_uploader(
        "Choose PDF",
        type="pdf"
    )



    if uploaded_file:


        st.success(
            "PDF selected"
        )


        if st.button(
            "🚀 Process PDF"
        ):


            with st.spinner(
                "Analyzing document..."
            ):


                # Save PDF

                with open(
                    "uploaded.pdf",
                    "wb"
                ) as f:

                    f.write(
                        uploaded_file.getbuffer()
                    )



                # Load

                docs = load_pdf(
                    "uploaded.pdf"
                )



                # Split

                chunks = split_text(
                    docs
                )



                # Embedding

                embedding_model = get_embedding_model()



                # Vector store

                vector_store = create_vector_store(
                    embedding_model
                )



                store_chunks(
                    vector_store,
                    chunks
                )



                # Retriever

                retriever = vector_store.as_retriever(
                    search_kwargs={
                        "k":3
                    }
                )



                # LLM

                llm = get_llm()



                # RAG

                st.session_state.rag = create_rag_pipeline(
                    retriever,
                    llm
                )



            st.success(
                "✅ PDF is ready!"
            )



    st.divider()



    st.markdown(
        """
        ## ✨ Features

        📚 PDF Understanding

        🔍 Semantic Search

        🤖 AI Answers

        ⚡ Fast Retrieval

        🔒 Secure

        """
    )





# ---------------- WELCOME ----------------


if len(st.session_state.messages)==0:


    st.markdown(
        """
        <div class="card">


        <h2>
        👋 Welcome to DocuMind AI
        </h2>


        Ask questions about your PDF:


        <br><br>


        🔹 Summarize the document

        <br>

        🔹 Explain concepts

        <br>

        🔹 Find important information

        <br>

        🔹 Create notes


        </div>

        """,

        unsafe_allow_html=True
    )





# ---------------- CHAT HISTORY ----------------


for message in st.session_state.messages:


    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )





# ---------------- CHAT ----------------


question = st.chat_input(
    "Ask something about your PDF..."
)



if question:


    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )


    with st.chat_message(
        "user"
    ):

        st.write(question)



    with st.chat_message(
        "assistant"
    ):


        if st.session_state.rag is None:


            answer = (
                "Please upload and process a PDF first."
            )


        else:


            with st.spinner(
                "Thinking..."
            ):


                answer = st.session_state.rag(
                    question
                )


                if isinstance(
                    answer,
                    dict
                ):

                    answer = answer["answer"]



        st.write(answer)



    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )