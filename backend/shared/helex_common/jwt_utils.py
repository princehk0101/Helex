import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional

ALGORITHM = "HS256"

def verify_token(token: str, secret_key: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None
