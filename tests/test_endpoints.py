import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.user import User

client = TestClient(app)

TEST_EMAIL = "endpoint_test_user@tesr.example"
TEST_PASSWORD = "correct-password123"

@pytest.fixture(autouse=True)
def clean_test_user():
    """
    Ensure no leftover test user exists before each test, and cleans up afterwards.
    autouse=True means this runs automaticallt for every test in this file without
    needing to be requested explicitly.
    """

    Base.metedata.create_all(bind=engine)
    db = SessionLocal()
    db.query(User).filter(User.email == TEST_EMAIL).delete()
    db.commit()
    db.close()

    yield

    db = SessionLocal()
    db.query(User).filter(User.email == TEST_EMAIL).delete()
    db.commit()
    db.close()


class TestRegisterEndpoint:
    def test_register_new_user_returns_201(self):
        response = client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )

        assert response.status_code == 201

    def test_register_new_user_creates_databse_row(self):
        client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )

        db = SessionLocal()
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        db.close()
        assert user is not None 

    def test_register_does_not_save_plaintext_password(self):
        client.post(
            "/register",
             json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )

        db = SessionLocal()
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        db.close()
        assert user.hashed_password != TEST_PASSWORD

    def test_register_duplicate_email_returns_409(self):
        #register first client
        client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )

        #second registration with same email
        response = client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": "different_password"},
        )
        assert response.status_code == 409

    def test_register_rejects_passwords_under_8_char(self):
        response = client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": "short"},
        )
        assert response.status_code == 422

    def test_register_rejects_incorrect_email_format(self):
        response = client.post(
            "/register",
            json = {"email": "not-email", "password": TEST_PASSWORD}
        )
        assert response.status_code == 422

    def test_register_reject_missing_fields(self):
        response = client.post(
            "/register",
            json = {"email": TEST_EMAIL}
        )

class TestLoginEndpoints:
    def _register_test_user(self):
        client.post(
            "/register",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
            )

    def test_login_with_correct_credentials_retunrs_200(self):
        self._register_test_user()
        response = client.post(
            "/login",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
            )
        assert response.status_code == 200

    def test_login_returns_a_login_token(self):
        self._register_test_user()
        response = client.post(
            "/login",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
            )
        body = response.json()
        assert "access_token" in body
        assert isinstance(body["access_token"], str)
        assert body["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self):
        self._register_test_user()
        response = client.post(
        "/login",
        json = {"email": TEST_EMAIL, "password": "wrong_password"},
        )
        assert response.status_code == 401

    def tets_login_wiht_nonexistent_email_returns_401(self):
        response = client.post(
        "/login",
        json = {"email": "non_existent@email.com", "password": TEST_PASSWORD},
        )
        assert response.status_code == 401

    def test_login_error_message_retuns_the_same_for_wrongPassword_and_noAccount(self):

        self._register_test_user()

        wrong_password_response = client.post(
        "/login",
        json = {"email": TEST_EMAIL, "password": "wrong_password"},
        )

        no_account_response = client.post(
        "/login",
        json = {"email": "non_registered@email.com", "password": TEST_PASSWORD},
        )

        assert wrong_password_response.status_code == no_account_response.status_code
        assert (
            wrong_password_response.json()["detail"]
            == no_account_response.json()["detail"]
        )


class TestFullAuthFlow:
    def test_register_test_login_then_token_is_valid(self):
        from app.Logic.security import decode_access_token

        client.post(
         "/register",
         json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},   
        )

        login_response = client.post(
            "/login",
            json = {"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )

        token = login_response.json()["access_token"]

        payload = decode_access_token(token)
        assert payload is not None

        db = SessionLocal()
        user = db.query(User).filter(User.email == TEST_EMAIL).first()
        db.close()

        assert payload["sub"] == str(user.id)
        