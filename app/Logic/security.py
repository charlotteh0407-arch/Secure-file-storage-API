import bcrypt


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

def verify_password(user_password: str, hashed_password: str) -> str:
    """
    check the users inputed password is matches the saved password
    """

    result = bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8') )
    return result