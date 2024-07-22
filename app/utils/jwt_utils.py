from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import PyJWKClient
from loguru import logger

from app.conf.config import settings


async def encode_jwt(
    payload: dict,
    client_secret: str = settings.API_SECRET,
    algorithm: str = settings.API_ALGORITHM,
    audience: str = settings.API_AUDIENCE,
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


def decode_jwt_token(token: str) -> dict:
    decoded = jwt.decode(
        token,
        settings.API_SECRET,
        algorithms=[settings.API_ALGORITHM],
        audience=settings.API_AUDIENCE,
    )
    return decoded


def decode_auth0_token(token: str) -> Any | None:
    try:
        url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_client = PyJWKClient(url)
        header = jwt.get_unverified_header(token)
        logger.debug(f"Token header: {header}")
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        logger.debug(f"Signing key: {signing_key}")
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[settings.AUTH0_ALGORITHM],
            audience=settings.AUTH0_API_AUDIENCE,
        )
        logger.info("Token successfully verified with Auth0.")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Auth0 verification failed: token is expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Auth0 verification failed: invalid token. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


def decode_jwt(token: str) -> dict:
    try:
        return decode_jwt_token(token)
    except Exception as e:
        logger.info(f"Exception occurred own token {e}")
        return decode_auth0_token(token)
