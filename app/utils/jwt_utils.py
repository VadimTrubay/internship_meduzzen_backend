from datetime import datetime, timedelta
import jwt

from app.conf.config import settings


async def encode_jwt(
    payload: dict,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = settings.AUTH0_ALGORITHM,
    audience: str = settings.AUTH0_API_AUDIENCE,
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
        exp=expire,
        iat=now,
        aud=audience,
    )
    encoded = jwt.encode(
        to_encode,
        client_secret,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    client_secret: str = settings.AUTH0_SECRET,
    algorithm: str = settings.AUTH0_ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        token,
        client_secret,
        algorithms=[algorithm],
        audience=settings.AUTH0_API_AUDIENCE,
    )
    return decoded
