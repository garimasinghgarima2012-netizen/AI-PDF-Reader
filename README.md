# 🧠 DocuMind AI — Neural PDF Assistant

DocuMind AI is a Retrieval-Augmented Generation (RAG) platform that enables semantic question-answering over uploaded PDF documents with exact page-referenced citations.

---

## 🚀 Key Features

- **Split-Screen Interface:** Read your PDF with an embedded viewer while interacting with the AI.
- **Embedded FAISS Vector Database:** Fast, local, reliable vector indexing with zero external database dependencies or subscription limits.
- **Ultra-Fast LLM Inference:** Powered by Groq LPU inference (`openai/gpt-oss-20b` and `qwen/qwen3.8-27b`).
- **Verifiable Citations:** Every answer includes exact page references and an expandable drawer to inspect the exact retrieved passages.
- **Conversational Memory:** Remembers recent conversation turns for multi-step questions and follow-ups.

---

## 🛠️ Quick Start (Local)

### 1. Prerequisites
- Python 3.10 or 3.11
- Groq API Key ([Get one free at console.groq.com](https://console.groq.com/keys))

### 2. Configure Environment
Create or edit your `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the App
```bash
streamlit run ui.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🐳 Docker Deployment

Build and run the containerized app:
```bash
docker build -t documind-ai .
docker run -p 8501:8501 --env-file .env documind-ai
```

---

## ☁️ Cloud Deployment Options

### Option A: Streamlit Community Cloud (Free)
1. Push this project to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your repository, set main file path to `ui.py`.
4. In **App Settings > Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   ```
5. Click **Deploy**.

### Option B: Render / Railway / Hugging Face Spaces
- **Render:** Deploy as a **Web Service** using Docker (the included `Dockerfile` is automatically detected). Add `GROQ_API_KEY` under Environment Variables.
- **Hugging Face Spaces:** Create a new Space with the **Streamlit** or **Docker** SDK, push the files, and set `GROQ_API_KEY` under Settings -> Repository Secrets.
