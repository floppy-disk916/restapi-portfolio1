from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from ..auth import check_current_token
from ..db import ASesDep
from ..models import Admin, Item
from ..repository import get_async_repo
from ..schemas import ItemAdd, ItemPublic, ItemUpdate

router = APIRouter(tags=["Item Operation"], prefix="/item")

# Decide what type of model you want for the repository
Repo = get_async_repo(Item, ItemPublic)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_item(
    item: ItemAdd,
    session: ASesDep,
    admin: Annotated[Admin, Depends(check_current_token)],
) -> ItemPublic:
    return await Repo.create_one(session=session, data=item)


@router.get("/")
async def get_item(name: str, session: ASesDep) -> ItemPublic:
    item_db = await Repo.get_one_by_id(session=session, _id=name, col="name")
    if item_db is None:
        raise HTTPException(status_code=404)
    return item_db


@router.patch("/")
async def partial_update_item(
    item: ItemUpdate, name: str, session: ASesDep
) -> ItemPublic:
    return await Repo.update_one_by_id(session=session, data=item, _id=name, col="name")


@router.put("/")
async def update_item(item: ItemUpdate, name: str, session: ASesDep) -> ItemPublic:
    return await Repo.update_one_by_id(session=session, data=item, _id=name, col="name")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    name: str,
    session: ASesDep,
    admin: Annotated[Admin, Depends(check_current_token)],
):
    return await Repo.remove_one_by_id(session=session, _id=name, col="name")
