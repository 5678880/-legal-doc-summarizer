from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from legalbackend import load_document, summarize_document, highlight_clauses, answer_query
import shutil
import os

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = load_document(file_path)

    if not documents:
        return {"error": "❌ No readable text found in document."}

    summary = summarize_document(documents)
    clauses = highlight_clauses(documents)

    return {
        "filename": file.filename,
        "summary": summary,
        "clauses": clauses,
    }

@app.post("/ask")
async def ask(question: str = Form(...)):
    files = os.listdir(UPLOAD_DIR)
    if not files:
        return {"error": "❌ No file uploaded yet."}

    last_file = os.path.join(UPLOAD_DIR, sorted(files)[-1])
    docs = load_document(last_file)
    answer = answer_query(docs, question)
    return {"answer": answer}

