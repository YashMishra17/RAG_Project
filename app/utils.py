import os
from fastapi import UploadFile

def save_file(file: UploadFile, upload_dir="uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path
