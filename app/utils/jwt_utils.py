from datetime import datetime, timedelta
import jwt
from loguru import logger

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
    encoded_jwt = jwt.encode(
        to_encode,
        client_secret,
        algorithm=algorithm,
    )
    return encoded_jwt


def decode_jwt_token(token: str, ) -> dict:
    decoded = jwt.decode(
        token,
        settings.AUTH0_SECRET,
        algorithms=[settings.AUTH0_ALGORITHM],
        audience=settings.API_AUDIENCE,
    )
    return decoded


def decode_auth0_token(token: str) -> dict:
    decoded = jwt.decode(
        token,
        settings.AUTH0_SECRET,
        algorithms=[settings.AUTH0_ALGORITHM],
        audience=settings.AUTH0_API_AUDIENCE,
    )
    return decoded


def decode_jwt(token: str) -> dict:
    try:
        return decode_jwt_token(token)
    except Exception as e:
        logger.info(f"Exception occurred own token {e}")
