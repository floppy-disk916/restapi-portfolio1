from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    APIKeyHeader
)

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    status,
)


from pydantic import ValidationError
from .db import ASesDep, AsyncSession
from sqlmodel import select
from .models import Admin, APIKey
from .schemas import Token, AdminPublic

from pwdlib import PasswordHash

from .config import settings

from datetime import datetime, UTC, timedelta
from jwt.exceptions import InvalidTokenError
import jwt

from typing import Annotated

JWT_ENCODE="RS256"
SECRET_KEY=settings.jwt_secret_key
JWT_PRIVATE_KEY=settings.jwt_private_key
JWT_PUBLIC_KEY=settings.jwt_public_key
JWT_ALGO=settings.jwt_algo
JWT_EXPIRE_MIN=settings.jwt_expire_min
API_KEY_EXPIRE_DAY=settings.api_key_expire_day


router = APIRouter(prefix="/auth")

oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=True)
hasher = PasswordHash.recommended()

def hash_password(password: str):
    return hasher.hash(password)

def verify_password(password: str, hashed: str):
    return hasher.verify(password, hashed)

async def get_admin(username: str) -> Admin:
    admin = await session.scalar(select(Admin).where(Admin.name == username))
    if admin is None:
        return None
    return admin

async def check_admin(session: AsyncSession, username: str, password: str) -> Admin:
    admin = await get_admin(username)
    if admin is None and verify_password(password, admin.password) == False:
        return None
    return admin

async def check_current_token(
    session: ASesDep,
    token: Annotated[str, Depends(OAuth2PasswordBearer)]
    ) -> Admin:

    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential", headers=message_headers)
    try:
        payload = jwt.decode(token, JWT_PRIVATE_KEY, algorithms=JWT_ALGO)
        username = payload.get("sub")
        if username is None:
            raise cred_exc
        
    except (InvalidTokenError, ValidationError):
        raise cred_exc
 
    admin = await get_admin(username)
    if admin is None:
        raise cred_exc
    return admin

import logging

logger = logging.getLogger(__name__)

async def check_api_key(
    session: ASesDep,
    key: Annotated[str, Depends(api_key_scheme)],
) -> str:
    key_db = await session.scalar(select(APIKey).where(APIKey.key == key))

    if not key_db:
        logger.error(f"key_db value: {key_db}\nhashed key value: {hashed}")
        raise HTTPException(status_code=401, detail="Invalid api key")
    if datetime.now(UTC) >= key_db.expire_date:
        raise HTTPException(status_code=401, detail="Expired api key")
    return key

async def create_token(username: str, expire_min: timedelta) -> str:
    if expire_min:
        expire = datetime.now(UTC) + expire_min
    else:
        expire = datetime.now(UTC) + timedelta(minutes=10)

    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, JWT_PRIVATE_KEY, algorithm=JWT_ENCODE)
    return token

@router.post("/token")
async def login(session: ASesDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    admin = await check_admin(session, form_data.username, form_data.password)
    if admin is None:
        raise HTTPException(status_code=404, detail="admin not found")
    expire_min = timedelta(minutes=JWT_EXPIRE_MIN)
    access_token = create_token(form_data.username, expire_min)
    token = Token(access_token=access_token, token_type="bearer")
    return token
