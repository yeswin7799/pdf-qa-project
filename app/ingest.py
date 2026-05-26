import os
import boto3
import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

def upload_to_s3(file_bytes: bytes, filename: str):
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
    s3.upload_fileobj(io.BytesIO(file_bytes), os.getenv("S3_BUCKET_NAME"), filename)
    print(f"Uploaded {filename} to S3.")

def download_from_s3(filename: str) -> io.BytesIO:
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
    buffer = io.BytesIO()
    s3.download_fileobj(os.getenv("S3_BUCKET_NAME"), filename, buffer)
    buffer.seek(0)
    return buffer

def extract_text_from_pdf(file_source) -> str:
    reader = PdfReader(file_source)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    return full_text

def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)
    return embeddings.tolist()

def store_in_chroma(chunks: list[str], embeddings: list[list[float]], collection_name: str = "pdf_chunks"):
    chroma_client = chromadb.PersistentClient(path="./data/chroma_store")
    try:
        chroma_client.delete_collection(name=collection_name)
        print("Old collection deleted.")
    except:
        pass

    collection = chroma_client.get_or_create_collection(name=collection_name)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB.")

def ingest(file_bytes: bytes, filename: str):
    print(f"Uploading {filename} to S3...")
    upload_to_s3(file_bytes, filename)

    print("Downloading from S3 for processing...")
    pdf_buffer = download_from_s3(filename)

    print("Extracting text...")
    text = extract_text_from_pdf(pdf_buffer)

    print("Splitting into chunks...")
    chunks = split_text(text)
    print(f"  → {len(chunks)} chunks created")

    print("Embedding chunks...")
    embeddings = embed_texts(chunks)

    print("Storing in ChromaDB...")
    store_in_chroma(chunks, embeddings)

    print("Ingestion complete!")    