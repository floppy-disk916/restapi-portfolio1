from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security import (
    APIKeyHeader,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import ValidationError
from sqlmodel import select

from .config import settings
from .db import ASesDep, AsyncSession
from .models import Admin, APIKey
from .schemas import Token

JWT_ENCODE = "RS256"
SECRET_KEY = settings.jwt_secret_key
JWT_PRIVATE_KEY = settings.jwt_private_key
JWT_PUBLIC_KEY = settings.jwt_public_key
JWT_ALGO = settings.jwt_algo
JWT_EXPIRE_MIN = settings.jwt_expire_min
API_KEY_EXPIRE_DAY = settings.api_key_expire_day


router = APIRouter(prefix="/auth", include_in_schema=False)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=True)
hasher = PasswordHash.recommended()


def hash_password(password: str):
    return hasher.hash(password)


def verify_password(password: str, hashed: str):
    return hasher.verify(password, hashed)


async def get_admin(session: AsyncSession, username: str) -> Admin:
    admin = await session.scalar(select(Admin).where(Admin.name == username))
    if admin is None:
        return None
    return admin


async def check_admin(session: AsyncSession, username: str, password: str) -> Admin:
    admin = await get_admin(session, username)
    if admin is None or verify_password(password, admin.password) == False:
        return None
    return admin


async def check_current_token(
    session: ASesDep, token: Annotated[str, Depends(oauth_scheme)]
) -> Admin:

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credential",
    )
    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=JWT_ALGO)
        username = payload.get("sub")
        if username is None:
            raise cred_exc

    except (InvalidTokenError, ValidationError):
        raise cred_exc

    admin = await get_admin(session, username)
    if admin is None:
        raise cred_exc
    return admin


from sqlalchemy.orm import selectinload

async def check_api_key(
    session: ASesDep,
    key: Annotated[str, Depends(api_key_scheme)],
) -> Admin:
    
    admin = await session.scalar(select(Admin).where(Admin.api_keys.any(APIKey.key == key)).options(selectinload(Admin.api_keys)))

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin


async def create_token(username: str, expire_min: timedelta) -> str:
    if expire_min:
        expire = datetime.now(UTC) + expire_min
    else:
        expire = datetime.now(UTC) + timedelta(minutes=10)

    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, JWT_PRIVATE_KEY, algorithm=JWT_ENCODE)
    return token

@router.post("/login")
async def login(
    session: ASesDep,
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    admin = await check_admin(session, form_data.username, form_data.password)
    if admin is None:
        raise HTTPException(status_code=404, detail="admin not found")
    expire_min = timedelta(minutes=JWT_EXPIRE_MIN)
    access_token = await create_token(form_data.username, expire_min)
    token = Token(access_token=access_token, token_type="bearer")
    return token

@router.post("/revoke", include_in_schema=False)
async def revoke_token(
    session: ASesDep,
    request: Request,
    admin: Annotated[Admin, Depends(check_current_token)]
):
    pass
