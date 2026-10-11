from langchain_groq import ChatGroq
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_llm(model_name="openai/gpt-oss-20b", temperature=0.1):
    """
    Initializes and returns the ChatGroq LLM instance.
    Checks Streamlit secrets, config module, and environment variables.
    """
    api_key = None

    # 1. Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    # 2. Try config module (if available)
    if not api_key:
        try:
            import config
            api_key = getattr(config, "GROQ_API_KEY", None)
        except Exception:
            pass

    # 3. Try os.getenv
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. Please add it to your .env file or Streamlit secrets."
        )

    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )

    return llm