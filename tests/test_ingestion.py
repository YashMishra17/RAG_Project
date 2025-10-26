from app.ingestion import process_document
from pathlib import Path

def test_process_document_txt(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Hello world. " * 200)
    n = process_document(str(p))
    assert n > 0
