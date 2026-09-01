import pytest
from fastapi import HTTPException
from app.Logic.security import(
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.api.auth import get_current_user

@pytest.fixture
def db_session():
    """Provides a database session for a test, and cleans up any test data afterwards
    so tests don't leave junk behind or interfere with each other"""

    Base.metadata.create_all(bind=engine)
    session = SessionLocal
    yield session
    session.query(User).filter(User.email.like("%@test.example%")).delete(
        synchronize_session=False
    )
    session.commit()
    session.close()


@pytest.fixture
def test_user(db_session):
    """Creates a reusable test user in the database"""
    user = User(
        email = "test_user@test.example",
        hashed_password = hash_password("correct-password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

#Password Hashing (Logic/security.py)

class TestPasswordHashing:
    def test_hash_password_returns_a_string(self):
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)

    def test_hash_password_is_not_the_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_password_correct_password_returns_true(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_password_wrong_password_returns_false(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

#JWT creation / decoding (Logic/security.py)
class TestJWT:
    def test_create_access_token_returns_a_string(self):
        token = create_access_token(1)
        assert isinstance(token, str)

    def test_decode_access_token_returns_correct_user_id(self):
        token = create_access_token(1)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "!"

    def test_decode_access_token_users_get_different_tokens(self):
        token_1 = create_access_token(1)
        token_2 = create_access_token(2)
        assert token_1 != token_2
        assert decode_access_token(token_1)["sub"] == "1"
        assert decode_access_token(token_2)["sub"] == "2"

    def test_decode_access_token_rejects_garbage_token(self):
        result = decode_access_token("this.is.not.a.real.token")
        assert result is None

#get_current_user dependency api/auth.py

class TestGetCurrentUser:
    def test_valide_token_returns_correct_user(self, db_session, test_user):
        token = create_access_token(test_user.id)
        result = get_current_user(token=token, db=db_session)
        assert result.email == test_user.email

    def test_invalid_token_raises_401(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="invalid.token", db=db_session)
        assert exc_info.value.status_code == 401

    def test_token_for_nonexistent_user_raises_401(self, db_session):
        token = create_access_token(9999)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)
        assert exc_info.value.status_code == 401