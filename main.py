import os
import hashlib
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from pdf_loader import load_pdf
from embedding import get_embedding_function
from vectorstore import create_vectorstore, load_vectorstore
from retriever import get_retriever, retrieve_chunks
from rag import rag_chain

load_dotenv()

# Track vectorstore paths created this session
state = {"retriever": None, "pdf_name": None, "last_answer": None, "vectorstore_path": None}

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def cleanup():
    """Delete vectorstore and uploaded_pdfs on shutdown."""
    if state["vectorstore_path"] and os.path.exists(state["vectorstore_path"]):
        shutil.rmtree(state["vectorstore_path"])
        print(f"🗑️ Deleted vectorstore: {state['vectorstore_path']}")
    if os.path.exists("uploaded_pdfs"):
        shutil.rmtree("uploaded_pdfs")
        print("🗑️ Deleted uploaded_pdfs folder")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # App runs here
    cleanup()  # Runs on shutdown

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    save_dir = "uploaded_pdfs"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    with open(save_path, "wb") as f:
        f.write(await file.read())

    try:
        file_hash = get_file_hash(save_path)
        vectorstore_path = f"app_vectorstore_{file_hash}"

        pages = load_pdf(save_path)
        vectorstore = create_vectorstore(pages, get_embedding_function(), vectorstore_path)

        state["retriever"] = get_retriever(vectorstore)
        state["pdf_name"] = file.filename
        state["last_answer"] = None
        state["vectorstore_path"] = vectorstore_path

    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    return {"message": f"{file.filename} processed successfully"}


class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if state["retriever"] is None:
        raise HTTPException(status_code=400, detail="No PDF uploaded yet")

    answer = rag_chain(request.question, state["retriever"], state["last_answer"])
    state["last_answer"] = answer
    return {"answer": answer}


@app.get("/status")
async def status():
    return {
        "pdf_loaded": state["retriever"] is not None,
        "pdf_name": state["pdf_name"]
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")