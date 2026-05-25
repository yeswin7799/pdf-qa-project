# app/generate.py

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

#client = OpenAI()

def build_context(chunks: list[str]) -> str:
    return "\n\n".join(chunks)

def generate(question: str, chunks: list[str]) -> str:
    client = OpenAI()
    context = build_context(chunks)

    system_prompt = """You are a precise document assistant. Your job is to answer questions strictly based on the context provided below.

Rules you must follow:
1. Only use information from the provided context. Do not use any outside knowledge.
2. If the answer is not in the context, respond with exactly: "The document does not contain information about that."
3. Be concise. Answer in 1-3 sentences unless a list is clearly more appropriate.
4. Never start your answer with phrases like "Based on the context..." or "According to the document...". Just answer directly.

Example:
Question: What programming languages does the person know?
Answer: The person knows Python, JavaScript, and SQL.

Now answer the user's question using only the context provided."""

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )

    return response.choices[0].message.content