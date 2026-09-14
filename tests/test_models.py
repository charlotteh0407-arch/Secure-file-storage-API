import pytest
from app.database import SessionLocal, Base, engine
from app.models.file import File
from app.models.user import User

@pytest.fixture
def db_session():
    Base.metatdata.create_all(bind=engine)
    session = SessionLocal()
    yield session

    session.query(File).filter(
        File.original_filename.like("phase1_test_%")
    ).delete(synchronize_session=False)
    session.query(User).filter(
        User.email.like("%@phase1_test.example")
    ).delete(synchronize_session=False)
    session.commit()
    session.close()

class TestUserModel:
    def test_can_reate_a_user(self, db_session):
        user = User(
            email="test@phase1_test.example",
            hashed_password="fakehash123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@phase1_test.example"

    def test_user_id_is_auto_assigned(self, db_session):
        user = User(
                email="test@phase1_test.example",
                hashed_password="fakehash123"
            )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert isinstance(user.id, int)

    def test_created_at_auto_generates(self, db_session):
        user = User(
                email="test@phase1_test.example",
                hashed_password="fakehash123"
            )
                
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.created_at is not None

    def test_duplicate_email_is_rejected_but_database(self, db_session):
        user1 = User(
            email= "duplicate_email@test.example",
            hashed_password="fakehash"
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            email="uplicate_email@test.example",
            hashed_password="differenthashpassword"
        )
        db_session.add(user2)

        with pytest.raises(Exception):
            db_session.commit()

        db_session.rollback()

class TestFileModel:
    def test_can_create_a_file_linked_to_a_user():
        user = User(
            email="file_owner@test.example",
            hashed_password="fakehash"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        file = File(
            owner_id=user.id,
            original_filename = "test_filename.pdf",
            storage_key= "test_storage_key.pdf",
            size=1024,
            mime_type="application/pdf",
        )
        db_session.add(file)
        db_session.commit()
        db_session.refresh(file)

        assert file.id is not None
        assert file.owner_id == user.id

    def test_file_ownership_works(self, db_session):
        user = User(
            email="file_owner@test.example",
            hashed_password="fakehash"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        file = File(
        owner_id=user.id,
        original_filename = "test_filename.pdf",
        storage_key= "test_storage_key.pdf",
        size=1024,
        mime_type="application/pdf",
        )

        db_session.add(file)
        db_session.commit()
        db_session.refresh(file)

        assert file.owner.email == "file_owner@test.example"
        assert file in user.files

    def test_deleted_at_defaults_to_None(self, db_session):
        user = User(
            email="file_owner@test.example",
            hashed_password="fakehash"
        )
                
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
                
        file = File(
            owner_id=user.id,
            original_filename = "test_filename.pdf",
            storage_key= "test_storage_key.pdf",
            size=1024,
            mime_type="application/pdf",
        )
        
        db_session.add(file)
        db_session.commit()
        db_session.refresh(file)

        assert file.deleted_at is None