from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import SessionLocal, engine
from .models import Base, Document
from .utils import save_file
from .ingestion import process_document, get_chunks_by_indices
from .retrieval import query_system, generate_response

Base.metadata.create_all(bind=engine)
app = FastAPI(title="RAG Demo for VS Code")

class QueryIn(BaseModel):
    query: str

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    db: Session = SessionLocal()
    uploaded_docs = []
    for file in files:
        path = save_file(file)
        try:
            chunks = process_document(path)
            doc = Document(filename=file.filename, chunks=chunks)
            db.add(doc)
            db.commit()
            uploaded_docs.append({"filename": file.filename, "chunks": chunks})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse({"uploaded": uploaded_docs})

@app.get("/metadata")
def get_metadata():
    db: Session = SessionLocal()
    docs = db.query(Document).all()
    return [{"filename": d.filename, "chunks": d.chunks, "uploaded_at": d.uploaded_at.isoformat()} for d in docs]

@app.post("/query")
def query_endpoint(payload: QueryIn):
    q = payload.query
    indices = query_system(q)
    chunks_texts = get_chunks_by_indices(indices)
    answer = generate_response(chunks_texts, q)
    return {"answer": answer, "sources": indices}
