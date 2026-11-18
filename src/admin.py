import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from .auth import hash_password
from .config import settings
from .db import ASesDep, get_async_repo
from .models import Admin, APIKey
from .schemas import AdminForm

router = APIRouter(prefix="/admin", include_in_schema=False)
templates = Jinja2Templates(directory="./src/templates")


@router.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")


AdminRepo = get_async_repo(Admin)
APIKeyRepo = get_async_repo(APIKey)


def generate_api_key(length: int = 32) -> str:
    alphabets = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabets) for _ in range(length))


@router.post("/register")
async def get_api_key(
    session: ASesDep,
    data: Annotated[AdminForm, Form()],
) -> str:

    data.password = hash_password(data.password)

    key: str = generate_api_key()

    expire_date = datetime.now(UTC) + timedelta(days=settings.api_key_expire_day)
    if settings.api_key_expire_day:
        expire_date = datetime.now(UTC) + timedelta(days=30)

    admin = await AdminRepo.create_one(
        session=session,
        data=data,
    )

    api_key = APIKey(
        admin_id=admin.id,
        expire_date=expire_date,
        key=key,
    )

    await APIKeyRepo.create_one(
        session=session,
        data=api_key,
    )

    return key


"""
@router.post("/register")
async def get_api_key(
    data: Annotated[AdminForm, Form()],
    ) -> str:
    


@router.get("/me")
async def get_current_admin(
    session: ASesDep,
    admin: Annotated[Admin, Depends(check_current_token),
    ):

@router.put()
@router.patch()
@router.delete()
"""
