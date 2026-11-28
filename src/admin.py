from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from .auth import hash_password, check_api_key
from .db import ASesDep
from .models import Admin, APIKey
from .repository import get_async_repo
from .schemas import AdminForm, AdminAdd, APIKeyAdd

router = APIRouter(prefix="/admin", include_in_schema=False)
templates = Jinja2Templates(directory="./src/templates")


AdminRepo = get_async_repo(Admin, Admin, child_model="api_key")
APIKeyRepo = get_async_repo(APIKey, APIKey, child_model="admin")


@router.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")



@router.post("/register")
async def get_api_key(
    session: ASesDep,
    data: Annotated[AdminForm, Form()],
) -> str:

    admin_data = AdminAdd.model_validate(data.model_dump())

    admin = await AdminRepo.create_one(
        session=session,
        data=admin_data,
    )

    api_key_data = APIKeyAdd(
        admin_id=admin.id,
    )

    api_key = await APIKeyRepo.create_one(
        session=session,
        data=api_key_data,
    )


    return api_key.key

@router.get("/me")
async def get_current_admin(
    session: ASesDep,
    admin: Annotated[Admin, Depends(check_api_key)],
    ) -> AdminPublic:
        return AdminPublic.model_validate(admin)
