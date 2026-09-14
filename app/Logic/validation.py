import os
from fastapi import HTTPException, status
import uuid

MAX_FILE_SIZE = 25 # in MB
FILE_SIGNATURES = {
    "pdf": [b"%PDF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "zip": [b"PK\x03\x04"],
    "docx": [b"PK\x03\x04"],
}
ALLOWED_FILE_EXTENSIONS = tuple(FILE_SIGNATURES.keys())

def calc_file_size(file) -> float:
    file_size_in_MB = os.path.getsize(file)/ (1024*1024) # Will need to be re-worked after as the upload file will not be saved yet, therefore have no path
    return file_size_in_MB

def get_file_extension(file_name) -> str:

    split_tup = os.path.splitext(file_name)
    file_extension = split_tup[1].lstrip(".")
    return file_extension

def validate_file_size(file) -> bool:

    file_size = calc_file_size(file)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file is too big"
        )

    return True #the file is the correct size
 
def validate_file_extension(file_name) -> bool:

    file_extension = get_file_extension(file_name)

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file is not in the accpeted format"
        )

    return True

def validate_file_content(file_bytes:bytes, extension: str) -> bool:

    extension = extension.lower().lstrip(".")
    if extension not in FILE_SIGNATURES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content could not be validated for this type"
        )

    valid_signtures = FILE_SIGNATURES[extension]
    return any(file_bytes.startswith(sig) for sig in valid_signtures)

def generate_storage_key(extension: str) ->str:

    return f"{uuid.uuid4()}.{extension}"