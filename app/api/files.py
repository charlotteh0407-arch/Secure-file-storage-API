from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.file import File as FileModel
from app.api.auth import get_current_user
from app.Logic.encryption import encrypt_file, ENCRYPTION_KEY
from app.Logic.validation import (
    get_file_extension,
    validate_file_content,
    validate_file_size,
    validate_file_extension,
    generate_storage_key,
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/files/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),):

    validate_file_extension(file.filename)
    extension = get_file_extension(file.filename)

    plaintext_bytes = await file.read()

    size_in_MB = len(plaintext_bytes) / (1024*1024)
    if size_in_MB > 25:
        raise HTTPException(
            status_code=400,
            detail= "File is too big"
        )

    validate_file_content(plaintext_bytes, extension)

    storage_key = generate_storage_key(extension)

    encrypted_bytes = encrypt_file(ENCRYPTION_KEY, plaintext_bytes)

    new_file = FileModel(
        owner_id = current_user.id
        original_filename = file.filename
        storage_key = storage_key
        size = len(plaintext_bytes)
        mime_type = file.content_type
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return{
        "id": new_file.id,
        "filename": new_file.original_filename,
        "size": new_file.size,
        "uploaded_at": new_file.uploaded_at,
    }
