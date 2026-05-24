# main.py

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from app.ingest import ingest
from app.retrieve import retrieve
from app.generate import generate

app = FastAPI()

@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_path = f"./data/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the ingestion pipeline
    ingest(temp_path)

    return {"message": f"Successfully ingested {file.filename}"}

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(request: AskRequest):
    chunks = retrieve(request.question, top_k=6)
    answer = generate(request.question, chunks)
    return {"answer": answer}

