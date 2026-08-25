from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.database import SessionLocal
from app.models.user import User
from app.Logic.security import decode_access_token, verify_password, create_access_token
from pydantic import BaseModel, EmailStr, Field
from app.Logic.security import hash_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str=Depends(oauth2_scheme), db: Session = Depends(get_db)) ->User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user

class registerRequest(BaseModel):
    email: EmailStr = Field(description= "Email must contain @ symbol")
    password: str = Field(min_length = 8, description="Password must be at least 8 characters long")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: registerRequest, db: Session = Depends(get_db)):

    exisitng_user = db.query(User).filter(User.email == payload.email).first()
    if exisitng_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_pass = hash_password(payload.password)

    new_user = User(
        email = payload.email,
        hashed_password = hashed_pass,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print("REGISRATION ERROR:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while creating your account"
        )

    return {"message": "Account created successfully"}

@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: registerRequest, db: Session = Depends(get_db)):

    email_check = db.query(User).filter(User.email == payload.email).first()
    if email_check:
        password_check = verify_password(payload.password, email_check.hashed_password)
        if password_check:
            access_token = create_access_token(email_check.id)
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid credentials"
            )
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid credentials"
        )
