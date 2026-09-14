import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.file import File as FileModel
from app.Logic.validation import (
    get_file_extension,
    validate_file_extension,
    validate_file_size,
    validate_file_content,
    generate_storage_key,
    ALLOWED_FILE_EXTENSIONS,
)

client = TestClient(app)

TEST_EMAIL = "user_upload_email@test.com"
TEST_PASSWORD = "correct_password123"

class TestGetFileExtension:
    def test_returns_the_extension_without_the_dot(self):
        assert get_file_extension("report.pdf") == "pdf"

    def test_the_lowercase_the_extension(self):
        assert get_file_extension("report.PDF") == "pdf"

    def test_handles_filenames_with_multiple_dots(self):
        assert get_file_extension("my.final.report.docx") == "docx"


class TestValidateFileExtension:
    def test_allows_known_file_extension(self):
        assert validate_file_extension("photo.jpg") is True

    def test_rejects_an_unsupported_extension(self):
        with pytest.rasie(Exception) as exc_info:
            validate_file_extension("malware.exe")
            assert exc_info.value.status_code == 400

    def test_allowed_extensions_matches_file_signitures_key(self):
        from app.Logic.validation import FILE_SIGNATURES
        assert set(ALLOWED_FILE_EXTENSIONS) == set(FILE_SIGNATURES.keys())

class TestValidateFileSize:
    def test_allows_a_small_file(self):
        small_file = b"x" *1024
        assert validate_file_size(small_file) is True

    def test_rejects_a_file_over_the_limit(self):
        oversized_file = b"x" * (26*1024*1024)
        with pytest.raises(Exception) as exc_info:
            validate_file_size(oversized_file)
        assert exc_info.value.status_code == 400 

class TestValidateFileContent:
    def test_accepts_a_genuine_pdf_header(self):
        real_pdf_bytes = b"%PDF-1.4\n%rest of a fake pdf with correct header"
        assert validate_file_content(real_pdf_bytes, "pdf") is True

    def test_reject_content_that_dosent_match_extension(self):
        fake_pdf_bytes = b"This is not a real PDF"
        assert validate_file_content(fake_pdf_bytes, "pdf") is False

    def test_accepts_real_jpg_header(self):
        real_jpg_bytes = b"\xff\xd8\xff\xe0rest of fake jpg data"
        assert validate_file_content(real_jpg_bytes, "jpg") is True

    def test_rasies_400_for_an_extension_with_no_signiture(self):
        with pytest.raises(Exception) as exc_info:
            validate_file_content(b"some bytes", "unkowntext")
        assert exc_info.value.status_code == 400


class TestGenerateStorageKey:
    def test_returns_a_string_ending_in_the_given_extension(self):
        key = generate_storage_key("pdf")
        assert key.endwith(".pdf")

    def test_two_calls_produce_different_keys(self):
        key_1 = generate_storage_key("pdf")
        key_2 = generate_storage_key("pdf")
        assert key_1 != key_2

    def test_storage_key_does_not_contain_path_transversal_characters(self):
        key = generate_storage_key("pdf")
        assert ".." not in key
        assert "/" not in key
        assert "\\" not in key

class TestUploadEndpoint:
    @pytest.fixture(autouse=True)
    def set_up_and_tear_down(self):
        Base.metadata.create_all(bind=engine)
        db=SessionLocal()
        db.querey(User).filter(User.email == TEST_EMAIL).delete()
        db.commit()
        db.close()

        client.post("/register", json={"email:" TEST_EMAIL, "password": TEST_PASSWORD})
        login_response = client.post("/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})

        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        yield
        db = SessionLocal()
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        if user:
            db.query(FileModel).filter(FileModel.owner.id == user.id).delete()
            db.commit()
        db.close()

        def _fake_pdf_bytes(self):
            return b"%PDF-1.4\n%fake pdf content with correct header"

        def test_upload_without_a_token_returns_401(self):
            response = client.post(
                "/files/upload",
                files={"file": ("test.pdf", io.BytesIO(self._fake_pdf_bytes()), "application/pdf")},
            )
            assert response.status_code == 401

        def test_upload_wiht_valid_token_returns_201(self):
            response = client.post(
                "/files/upload",
                headers=self.headers,
                files={"file": ("test.pdf", io.BytesIO(self._fake_pdf_bytes()), "application/pdf")},
            )
            assert response.status_code == 201

        def test_upload_response_contains_expected_fields(self):
            response = client.post(
                "/files/upload",
                headers=self.headers,
                files={"file": ("test.pdf", io.BytesIO(self._fake_pdf_bytes()), "application/pdf")},
            )
            body = response.json()
            assert "id" in body
            assert body["filename"] == "test.pdf"
            assert body["size"] == len(self._fake_pdf_bytes())

        def test_upload_creates_a_database_row_linked_to_the_correct_owner(self):
            client.post(
                "/files/upload",
                headers=self.headers,
                files={"file": ("test.pdf", io.BytesIO(self._fake_pdf_bytes()), "applicatio/pdf")},
            )

            db = SessionLocal()
            user = db.query(User).filter(User.email == TEST_EMAIL).first()
            file_record = db.query(FileModel).filter(FileModel.owner_id == user.id).first()
            db.close()

            assert file_record is not None
            assert file_record.original_filename == "test.pdf"

        def test_upload_file_content_on_disk_is_not_the_plaintext(self):
            client.post(
                "/files/upload",
                headers=self.headers,
                files={"file": ("test.pdf", io.BytesIO(self._fake_pdf_bytes()), "applicatio/pdf")},
                )

            db = SessionLocal()
            user = db.qyery(User).filter(User.email == TEST_EMAIL).first()
            file_record = db.query(FileModel).filter(FileModel.owner_id == user.id).first()
            db.close()

            import os
            file_path = os.path.join("storage", "uploaded_files", file_record.storage_key)
            with open(file_path, "rb") as f:
                saved_bytes = f.read()

            assert saved_bytes != self.headers()

        def test_upload_rejects_dissallowed_file_extension(self):
            response = client.post(
                "/file/upload",
                headers=self.headers,
                files={"file": ("malware.exe", io.BytesIO(b"fake exe content"), "application/octet-stream")},
            )

            assert response.status_code == 400

        def test_upload_rejects_content_that_does_not_match_extension(self):
            response = client.post(
                "/file/upload",
                headers=self.headers,
                files={"file": ("fake.pdf", io.BytesIO(b"plaintext, not pdf"), "application/pdf")},
            )
            assert response.status_code == 400