import os
import numpy as np
import faiss
from .ingestion import embed_text, INDEX_FILE, EMBEDDING_DIM, get_chunks_by_indices

if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
else:
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    faiss.write_index(index, INDEX_FILE)

USE_DEMO = os.getenv("OPENAI_API_KEY", "") == ""
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

if not USE_DEMO:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

def query_system(query: str, top_k: int = 5):
    vec = np.array([embed_text(query)], dtype="float32")
    if index.ntotal == 0:
        return []
    D, I = index.search(vec, top_k)
    return I[0].tolist()

def generate_response(chunks_texts, query: str):
    if USE_DEMO:
        c0 = chunks_texts[0][:400] if chunks_texts else ""
        return f"DEMO ANSWER (no API key): Based on context: {c0}"

    prompt = "Use the following context to answer the question concisely.\n\n"
    for i, chunk in enumerate(chunks_texts):
        prompt += f"[Chunk {i+1}]: {chunk}\n"
    prompt += f"\nQuestion: {query}\nAnswer:"

    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.0,
    )
    return resp["choices"][0]["message"]["content"]
