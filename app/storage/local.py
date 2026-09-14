import os

STORAGE_DIR = "storage/uploaded_files" \
""
def save_encrypted_file(storage_key: str, encrypted_bytes: bytes) -> None:
    os.makedirs(STORAGE_DIR, exist_ok=True)

    file_path = os.path.join(STORAGE_DIR, storage_key)

    with open(file_path, mode="wb") as f:
        f.write(encrypted_bytes)
        