import os
import json
from pathlib import Path
from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import faiss
import hashlib

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = str(DATA_DIR / "faiss.index")
CHUNKS_FILE = str(DATA_DIR / "chunks.json")

EMBEDDING_DIM = 1536

USE_DEMO = os.getenv("OPENAI_API_KEY", "") == ""

if not USE_DEMO:
    try:
        from langchain.embeddings.openai import OpenAIEmbeddings
        embeddings_client = OpenAIEmbeddings()
    except Exception:
        USE_DEMO = True

def _ensure_index():
    if os.path.exists(INDEX_FILE):
        idx = faiss.read_index(INDEX_FILE)
    else:
        idx = faiss.IndexFlatL2(EMBEDDING_DIM)
        faiss.write_index(idx, INDEX_FILE)
    return idx

index = _ensure_index()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def _demo_embed(text: str):
    h = hashlib.sha256(text.encode()).digest()
    arr = (h * ((EMBEDDING_DIM // len(h)) + 1))[:EMBEDDING_DIM]
    vec = np.frombuffer(arr, dtype=np.uint8).astype("float32") / 255.0
    return vec

def embed_text(text: str):
    if USE_DEMO:
        return _demo_embed(text)
    v = embeddings_client.embed_query(text)
    return np.array(v, dtype="float32")

def _load_chunks():
    if os.path.exists(CHUNKS_FILE):
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_chunks(all_chunks: List[str]):
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False)

def process_document(file_path: str) -> int:
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        text_parts = []
        for p in reader.pages:
            t = p.extract_text()
            if t:
                text_parts.append(t)
        text = "\n".join(text_parts)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    chunks = text_splitter.split_text(text)
    if not chunks:
        return 0

    vectors = [embed_text(c) for c in chunks]
    vectors_np = np.array(vectors, dtype="float32")
    index.add(vectors_np)
    faiss.write_index(index, INDEX_FILE)

    existing = _load_chunks()
    existing.extend(chunks)
    _save_chunks(existing)

    return len(chunks)

def get_chunks_by_indices(indices):
    all_chunks = _load_chunks()
    texts = []
    for i in indices:
        if 0 <= i < len(all_chunks):
            texts.append(all_chunks[i])
    return texts
