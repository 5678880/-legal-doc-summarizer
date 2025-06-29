import os
import pytesseract
from pdf2image import convert_from_path
from docx import Document
from datetime import datetime
import csv

from llama_index.core import Document as LlamaDocument
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ✅ Setup: LLM + Embedding
llm = Ollama(model="llama3")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = llm
Settings.embed_model = embed_model

chat_history = []


def load_document():
    docs = []
    for filename in os.listdir("data"):
        filepath = os.path.join("data", filename)
        text = ""

        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

        elif filename.endswith(".docx"):
            doc = Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs])

        elif filename.endswith(".pdf"):
            try:
                from llama_index.readers.file import PDFReader
                reader = PDFReader()
                pdf_docs = reader.load_data(filepath)
                text = "\n".join([doc.text for doc in pdf_docs])
            except Exception:
                images = convert_from_path(filepath)
                for img in images:
                    text += pytesseract.image_to_string(img)

        if text.strip():
            docs.append(LlamaDocument(text=text))

    return docs


def build_index(documents):
    return VectorStoreIndex.from_documents(documents)


def save_to_log(filename, category, content):
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "session_log.csv")
    header = ["timestamp", "filename", "category", "content"]

    if not os.path.exists(log_path):
        with open(log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(),
                        filename, category, content])


def summarize_document(documents):
    if not documents:
        return "⚠️ No document to summarize. Please upload a valid file."
    index = build_index(documents)
    response = index.as_query_engine().query(
        "Summarize this legal document in simple terms.")
    summary = str(response)
    save_to_log("uploaded", "summary", summary)
    return summary


def highlight_clauses(documents):
    if not documents:
        return "⚠️ No document to analyze. Please upload a valid file."
    index = build_index(documents)
    response = index.as_query_engine().query(
        "List the important legal clauses and tag them under categories like Confidentiality, Termination, Liability, Dispute Resolution, etc. Explain each in plain language."
    )
    clauses = str(response)
    save_to_log("uploaded", "highlighted_clauses", clauses)
    return clauses


def answer_query(documents, query):
    global chat_history
    combined_text = "\n".join(
        [doc.text for doc in documents if doc.text.strip()])
    if not combined_text.strip():
        combined_text = "No usable text found in the uploaded document."

    history = "\n".join([f"User: {q}\nAI: {a}" for q, a in chat_history])

    prompt = f"""
You are a helpful AI with expertise in legal and general questions.
Always answer clearly, even if the question is not related to any document.

Uploaded Document:
{combined_text[:2000]}

Chat History:
{history}

User: {query}
AI:"""

    response = llm.complete(prompt).text.strip()
    chat_history.append((query, response))
    save_to_log("uploaded", "qa", f"Q: {query}\nA: {response}")
    return response
