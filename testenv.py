import os
from config import GROQ_API_KEY, GEMINI_API_KEY

def check_env():
    print("=== Environment Check ===")
    print("GROQ_API_KEY:", "Configured" if GROQ_API_KEY else "MISSING")
    print("GEMINI_API_KEY:", "Configured" if GEMINI_API_KEY else "Not configured (optional)")
    
    # Test FAISS
    try:
        from langchain_community.vectorstores import FAISS
        print("Vector Store: FAISS available and ready")
    except Exception as e:
        print("Vector Store error:", e)

if __name__ == "__main__":
    check_env()