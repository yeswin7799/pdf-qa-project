import os
from pypdf import PdfReader
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

#client = OpenAI()

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    return full_text

def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # each chunk is at most 500 characters
        chunk_overlap=50      # last 50 chars of one chunk repeat at start of next
    )
    return splitter.split_text(text)

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)
    return embeddings.tolist()

def store_in_chroma(chunks: list[str], embeddings: list[list[float]], collection_name: str = "pdf_chunks"):
    chroma_client = chromadb.PersistentClient(path="./data/chroma_store")
     # Delete old collection if it exists (avoids dimension mismatch)
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
    

def ingest(file_path: str):
    print(f"Reading PDF: {file_path}")
    text = extract_text_from_pdf(file_path)

    print("Splitting into chunks...")
    chunks = split_text(text)
    print(f"  → {len(chunks)} chunks created")

    print("Embedding chunks...")
    embeddings = embed_texts(chunks)

    print("Storing in ChromaDB...")
    store_in_chroma(chunks, embeddings)

    print("Ingestion complete!")
