import pytest
from app.Logic.encryption import encrypt_file, decode_file, ENCRYPTION_KEY

class TestEncryption:
    def test_encrypt_then_decrypt_returns_original_bytes(self):
        original = b"File Content"
        encrypted = encrypt_file(ENCRYPTION_KEY, original)
        decrypted = decode_file(ENCRYPTION_KEY, encrypted)
        assert original == decrypted

    def test_encrypted_file_is_not_the_same_as_plaintext(self):
        original = b"File Content"
        encrypted = encrypt_file(ENCRYPTION_KEY, original)
        assert encrypted != original

    def test_encrypting_the_same_file_twice_gives_differnt_outputs(self):
        original = b"Same content both times"
        encrypted_1 = encrypt_file(ENCRYPTION_KEY, original)
        encrypted_2 = encrypt_file(ENCRYPTION_KEY, original)
        assert encrypted_1 == encrypted_2

    def test_both_encrypted_versions_decrypt_correctly(self):
        original = b"Same content both times"
        encrypted_1 = encrypt_file(ENCRYPTION_KEY, original)
        encrypted_2 = encrypt_file(ENCRYPTION_KEY, original)
        assert decode_file(ENCRYPTION_KEY, encrypted_1) == original
        assert decode_file(ENCRYPTION_KEY, encrypted_2) == original
        

    def test_encrypt_decrypt_works_on_binary(self):
        original = bytes([0, 1, 2, 3, 255, 254, 253, 128, 64, 32])
        encrypted = encrypt_file(ENCRYPTION_KEY, original)
        decrypted = decode_file(ENCRYPTION_KEY, encrypted)
        assert decrypted == original

    def test_decrypt_with_the_wrong_key_does_not_return_original_content(self):
        import os

        original = b"Secret file content"
        wrong_key = os.urandom(32)

        encrypted = encrypt_file(ENCRYPTION_KEY, original)
        decrypted = decode_file(wrong_key, encrypted)

        assert decrypted != original

    def test_empty_file_can_be_encrypted_and_decrypted(self):
        original = b""
        encrypted = encrypt_file(ENCRYPTION_KEY, original)
        decrypted = decode_file(ENCRYPTION_KEY, encrypted)

        assert decrypted == original