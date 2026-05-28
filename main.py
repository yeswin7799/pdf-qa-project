from fastapi import FastAPI, UploadFile, File
from app.guardrails import validate_question
from pydantic import BaseModel
import logging

from app.ingest import ingest
from app.retrieve import retrieve
from app.generate import generate

# Configure logging — runs once when the app starts
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    logger.info(f"Ingest request received | filename={file.filename}")
    try:
        file_bytes = await file.read()
        result = ingest(file_bytes, file.filename)
        logger.info(f"Ingest successful | filename={file.filename}")
        return result
    except Exception as e:
        logger.error(f"Ingest failed | filename={file.filename} | error={str(e)}")
        raise

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(payload: AskRequest):
    logger.info(f"Question received | question={payload.question}")

    # Layer 1 — run guardrail before anything else
    is_valid, error_message = validate_question(payload.question)
    if not is_valid:
        logger.warning(f"Question rejected by guardrail | reason={error_message}")
        return {"answer": error_message}

    try:
        chunks = retrieve(payload.question)
        answer = generate(payload.question, chunks)
        logger.info(f"Answer generated | question={payload.question}")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Answer generation failed | question={payload.question} | error={str(e)}")
        raise