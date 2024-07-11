from datetime import datetime, timedelta
import bcrypt
import jwt
from app.conf.config import settings


async def encode_jwt(
    payload: dict,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = settings.AUTH0_ALGORITHM,
    expire_minutes: int = settings.TOKEN_EXPIRATION,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire, iat=now, iss=settings.ISSUER, aud=settings.AUTH0_API_AUDIENCE
    )
    try:
        encoded = jwt.encode(
            to_encode,
            client_secret,
            algorithm=algorithm,
        )
    except ValueError as e:
        print(f"Error encoding JWT: {e}")
        raise

    return encoded


def decode_jwt(
    token: str | bytes,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = "HS256",
) -> dict:
    try:
        decoded = jwt.decode(
            token,
            client_secret,
            algorithms=[algorithm],
            audience=settings.AUTH0_API_AUDIENCE,
        )
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        raise

    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )
