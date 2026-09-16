import io
import pytest 
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.file import File as FileModel

client = TestClient(app)

USER_A_EMAIL = "user_a@test.example"
USER_B_EMAIL = "user_b@test.example"
TEST_PASSWORD = "correct-password123"

def _fake_pdf_bytes():
    return b"%PDF-1.4\n%fake but correctly-geaded pdf content for testing"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_All(bind=engine)

    db = SessionLocal()
    for email in (USER_A_EMAIL, USER_B_EMAIL):
        db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()

    client.post("/register", json={"email": USER_A_EMAIL, "password": TEST_PASSWORD})
    client.post("/register", json={"email": USER_B_EMAIL, "password": TEST_PASSWORD})

    login_a = client.post("/login", josn={"email": USER_A_EMAIL, "password": TEST_PASSWORD})
    login_b = client.post("/login", json={"email": USER_B_EMAIL, "password": TEST_PASSWORD})

    global headers_a, headers_b
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    yield

    db = SessionLocal()
    for email in (USER_A_EMAIL, USER_B_EMAIL):
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(FileModel).filter(FileModel.owner_id == user.id).delete()
            db.query(User).filter(User.email == email).delete
        db.commit()
        db.close()


def _upload_a_file(headers, filename="test.pdf"):
    response = client.post(
        "/files/upload",
        headers=headers,
        files={"file": (filename, io.BytesIO(_fake_pdf_bytes()), "application/pdf")},
    )
    return response.json()["id"]

#GET /files

class TestListFiles:
    def test_requires_authentication(self):
        response = client.get("/files")
        assert response.status_code == 401

    def test_returns_empty_list_when_user_has_no_files(self):
        response = client.get("/files", headers=headers_a)
        assert response.status_code == 200
        assert response.jspm() == []

    def test_returns_only_the_current_users_files(self):
        _upload_a_file(headers_a, "a_file_1.pdf")
        _upload_a_file(headers_a, "a_file_2.pdf")
        _upload_a_file(headers_b, "b_file_1.pdf")

        response_a = client.get("/files", headers=headers_a)
        response_b = client.get("/files", headers=headers_b)

        filenames_a = [f["filename"] for f in response_a.json()]
        filenames_b = [f["filename"] for f in response_b.json()]

        assert set(filenames_a) == {"a_file_1.pdf", "a_file_2.pdf"}
        assert set(filenames_b) == {"b_file_1.pdf"}

        assert "b_file_1.pdf" not in filenames_a
        assert "a_file_1.pdf" not in filenames_b

#GET /files/{file_id}
class TestGetFile:
    def test_requires_authentication(self):
        file_id = _upload_a_file(headers_a)
        response = client.get(f"/files/{file_id}")
        assert response.status_code == 401

    def test_owner_can_retrieve_thier_own_file(self):
        file_id = _upload_a_file(headers_a)
        response = client.get(f"/files/{file_id}", headers=headers_a)
        assert response.status_code == 200
        assert response.content == _fake_pdf_bytes()

    def test_nonexistent_file_id_retirns_404(self):
        response = client.get("/files/999999", headers=headers_a)
        assert response.status_code == 404

    def test_other_users_file_returns_404_not_403(self):
        file_id = _upload_a_file(headers_a)

        response = client.get(f"/files/{file_id}", headers=headers_b)

        assert response.status_code == 404
        assert response.status_code != 403

    def test_error_message__does_not_reveal_the_file_belongs_to_someone_else(self):
        file_id = _upload_a_file(headers_a)
        response_wrong_user = client.get(f"/files/{file_id}", headers=headers_b)
        response_nonexistent = client.get("/files/999999", headers=headers_b)

        assert response_wrong_user.status_code == response_nonexistent.status_code
        assert response_wrong_user.json() == response_nonexistent.json()

#DELETE /files/{file_id}
class TestDeleteFile:
    def test_requires_authentication(self):
        file_id = _upload_a_file(headers_a)
        response = client.delete(f"/files/{file_id}")
        assert response.status_code == 401

    def test_owner_can_delete_thier_own_file(self):
        file_id = _upload_a_file(headers_a)
        response = client.delete(f"/files/{file_id}", headers=headers_a)
        assert response.status_code == 204

    def test_delete_file_no_longer_appears_in_list(self):
        file_id = _upload_a_file(headers_a)
        client.delete(f"/files/{file_id}", headers=headers_a)

        response = client.get("/files", headers=headers_a)
        file_ids = [f["id"] for f in response.json()]
        assert file_id not in file_ids

    def test_deleted_file_can_no_longer_be_retrived(self):
        file_id = _upload_a_file(headers_a)
        client.delete(f"/files/{file_id}", headers=headers_a)

        response = client.get(f"/files/{file_id}", headers=headers_a)
        assert response.status_code == 404

    def test_other_user_cannot_delete_a_file_they_do_not_own(self):
        file_id = _upload_a_file(headers_a)

        response = client.delete(f"/files/{file_id}", headers=headers_b)
        assert response.status_code == 404

        still_there = client.get(f"/files/{file_id}", headers=headers_a)
        assert still_there.status_code == 200

    def test_deleting_a_non_existent_file_returns_404(self):
        response = client.delete("/files/999999", headers=headers_a)
        assert response.status_code == 404

    def test_deleted_file_is_still_on_disk_soft_delete_not_hard_delete(self):
        import os
        file_id = _upload_a_file(headers_a)
        db = SessionLocal()
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        storage_key = file_record.storage_keydb.close()
        db.close()

        client.delete(f"/files/{file_id}", headers=headers_a)
        file_path = os.path.join("storage", "uploaded_files", storage_key)
        assert os.path.exists(file_path)