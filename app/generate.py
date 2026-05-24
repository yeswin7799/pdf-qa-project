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

    system_prompt = (
        "You are a helpful assistant. "
        "Answer the user's question using only the provided context. "
        "If the answer is not in the context, say 'I don't know based on the provided document.'"
    )

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )

    return response.choices[0].message.content