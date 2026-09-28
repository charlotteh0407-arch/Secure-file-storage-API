from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.user import User
from app.models.file import File as FileModel
from app.api.auth import get_current_user
from app.Logic.encryption import encrypt_file, decode_file, ENCRYPTION_KEY
from app.Logic.validation import (
    get_file_extension,
    validate_file_content,
    validate_file_size,
    validate_file_extension,
    generate_storage_key,
)
from app.storage.local import save_encrypted_file, read_encrypted_file


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
    validate_file_size(plaintext_bytes)
    validate_file_content(plaintext_bytes, extension)

    storage_key = generate_storage_key(extension)
    encrypted_bytes = encrypt_file(ENCRYPTION_KEY, plaintext_bytes)
    save_encrypted_file(storage_key, encrypted_bytes)

    new_file = FileModel(
        owner_id = current_user.id,
        original_filename = file.filename,
        storage_key = storage_key,
        size = len(plaintext_bytes),
        mime_type = file.content_type,
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

@router.get("/files")
def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    files = (
        db.query(FileModel)
        .filter(
            FileModel.owner_id == current_user.id,
            FileModel.deleted_at.is_(None),
        ).all()
        )
    return [
        {
            "id": f.id,
            "filename": f.original_filename,
            "size": f.size,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]

@router.get("/files/{file_id}")
def get_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),):
    file = (
        db.query(FileModel)
        .filter(
            FileModel.id == file_id,
            FileModel.owner_id == current_user.id,
            FileModel.deleted_at.is_(None),
        )
        .first()
    )

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "File not found"
        )

    encrypted_bytes = read_encrypted_file(file.storage_key)
    decrytped_bytes = decode_file(ENCRYPTION_KEY, encrypted_bytes)

    return Response(content=decrytped_bytes, media_type=file.mime_type)

@router.delete("/file/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    file = (
        db.query(FileModel)
        .filter(
            FileModel.id == file_id,
            FileModel.owner_id == current_user.id,
            FileModel.deleted_At.is_(None),
        )
        .first()
    )

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file.deleted_At = datetime.now(timezone.utc)
    db.commit()

    return None
