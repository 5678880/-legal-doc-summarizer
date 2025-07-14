# 🧾 Legal Document Simplifier & Analyzer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![LLM](https://img.shields.io/badge/Powered%20by-Ollama%20LLaMA3-yellowgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

An AI-powered web app that simplifies, summarizes, and analyzes legal documents using LLMs. Built with Streamlit, this app turns complex contracts into readable insights — for students, researchers, and legal tech enthusiasts.

---

## ✨ Features

- 📄 Upload `.pdf`, `.docx`, or `.txt` legal documents
- 🧠 AI-based summarization with markdown formatting
- ✍️ Clause extraction and explanation (e.g., Termination, Confidentiality)
- 💬 Natural language Q&A over document content
- 🔎 Jargon simplification in everyday language
- 📑 Clause-by-clause breakdown
- 🕵️ Entity extraction: people, orgs, dates, locations
- ⚖️ Document comparison with highlights

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/5678880/-legal-doc-summarizer.git
cd legal_doc_simplifier

## 🐳 Run with Docker

This project supports full Docker deployment for easy, cross-platform execution.

### ✅ Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Ollama](https://ollama.com/download) installed and **running on the host machine**
  - Start Ollama in a separate terminal using:
    ```bash
    ollama serve
    ```
  - Make sure your model (like `llama3`) is downloaded:
    ```bash
    ollama run llama3
    ```

---

### 🚀 How to Run

Follow these steps to build and launch the app in Docker:

#### 1. **Clone the repository**
```bash
git clone https://github.com/yourusername/legal-doc-simplifier.git
cd legal-doc-simplifier
```

#### 2. **Build the Docker image**
```bash
docker build -t legal-doc-summarizer .
```

#### 3. **Run the Docker container**
```bash
docker run -p 8501:8501 legal-doc-summarizer
```

#### 4. **Access the app in your browser**
```
http://localhost:8501
```

---

### 🛠️ Troubleshooting

#### ❌ "Bind for 0.0.0.0:8501 failed: port is already allocated"
- This means port 8501 is already in use.
- Run on a different port:
  ```bash
  docker run -p 8601:8501 legal-doc-summarizer
  ```
  → Then open: `http://localhost:8601`

#### ❌ Ollama connection error in app
- Ensure Ollama is running locally using:
  ```bash
  ollama serve
  ```
- Your `legal_backend.py` must include:
  ```python
  llm = Ollama(
      model="llama3",
      base_url="http://host.docker.internal:11434",
      request_timeout=120
  )
  ```
  ## 🔧 Running Backend without Docker (Local)

You can run the FastAPI backend directly using `uvicorn`.

### Step-by-step:

1. Install dependencies:

```bash
pip install -r requirements.txt


#### ❌ SSL or model download errors for HuggingFace
- This might be due to network issues inside Docker.
- Pre-download the model outside Docker if needed and mount the cache folder.

---

### 💬 Common Docker Commands

- Stop container:
  ```bash
  docker ps  # get container ID
  docker stop <container_id>
  ```

- Remove container/image:
  ```bash
  docker rm <container_id>
  docker rmi legal-doc-summarizer
  ```


