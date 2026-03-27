import hashlib

# Хеш пароля "1234" (вы можете заменить на свой)
PASSWORD_HASH = hashlib.sha256("1111".encode()).hexdigest()

def verify_password(password: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH