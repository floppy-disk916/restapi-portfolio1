from fastapi import APIRouter, status

from ..db import ASesDep, get_async_repo
from ..models import Item
from ..schemas import ItemAdd, ItemPublic, ItemUpdate

router = APIRouter(tags=["Item Operation"], prefix="/item")

# Decide what type of model you want for the repository
Repo = get_async_repo(Item)


@router.post("/")
async def add_item(item: ItemAdd, session: ASesDep) -> ItemPublic:
    return await Repo.create_one(session=session, data=item)


@router.get("/")
async def get_item(name: str, session: ASesDep) -> ItemPublic:
    return await Repo.get_one_by_id(session=session, _id=name, col="name")


@router.patch("/")
async def partial_update_item(
    item: ItemUpdate, name: str, session: ASesDep
) -> ItemPublic:
    return await Repo.update_one_by_id(session=session, data=item, _id=name, col="name")


@router.put("/")
async def update_item(item: ItemUpdate, name: str, session: ASesDep) -> ItemPublic:
    return await Repo.update_one_by_id(session=session, data=item, _id=name, col="name")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(name: str, session: ASesDep):
    return await Repo.remove_one_by_id(session=session, _id=name, col="name")
