import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = base64.b64decode(os.environ["ENCRYPTION_KEY"])

def encrypt_file(key: bytes, plaintext: bytes) -> bytes:

    iv = urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return iv + ciphertext

def decode_file(key: bytes, encrypted_data: bytes):

    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypt_data = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypt_data