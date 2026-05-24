# app/retrieve.py

from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()

#client = OpenAI()

def embed_query(query: str) -> list[float]:
    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query]
    )
    return response.data[0].embedding

def retrieve(query: str, top_k: int = 3) -> list[str]:
    query_vector = embed_query(query)

    chroma_client = chromadb.PersistentClient(path="./data/chroma_store")
    collection = chroma_client.get_or_create_collection(name="pdf_chunks")

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )

    chunks = results["documents"][0]

    # Temporary debug — remove later
    print("\n--- Retrieved chunks ---")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:\n{chunk}\n")
    print("------------------------\n")

    return chunks
