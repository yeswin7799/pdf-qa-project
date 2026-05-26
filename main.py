from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.ingest import ingest
from app.retrieve import retrieve
from app.generate import generate

app = FastAPI()

@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()
    ingest(file_bytes, file.filename)
    return {"message": f"Successfully ingested {file.filename}"}

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: AskRequest):
    chunks = retrieve(request.question, top_k=6)
    answer = generate(request.question, chunks)
    return {"answer": answer}