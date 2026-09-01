import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "secret-key"#change to enviroment variable later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def gen_salt():
    """
    Generates the test string that will be used to salt the password
    Returns: salt: string
    """
    salt = bcrypt.gensalt()
    return salt


def hash_password(password: str) -> str:
    """
    Hashes the password
    Parameters: password: The password given by the user that they want to salt
    """
    password_bytes = password.encode('utf-8')
    salt = gen_salt()
    hash_password = bcrypt.hashpw(password_bytes, salt)
    return hash_password.decode('utf-8')

def verify_password(user_password: str, hashed_password: str) -> bool:
    """
    check the users inputed password is matches the saved password
    Parameters:
    user_password - the password the users logging in wit
    hashes_password - hashed password from the db

    Returns:
    True if passwords match
    false if passwords do not match
    """

    result = bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8') )
    return result

def create_access_token(user_id: int) -> str:

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm = ALGORITHM
    )
    return token

def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None