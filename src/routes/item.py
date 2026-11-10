from fastapi import APIRouter, status, HTTPException
from ..models import Item, ItemPublic, ItemAdd, ItemUpdate
from ..db import ASesDep
from typing import Annotated

router = APIRouter(tags=["Item Operation"], prefix="/item")


@router.post("/")
async def add_item(item: ItemAdd, session: ASesDep) -> ItemPublic:
    session.add(item)
    return item

@router.get("/")
async def get_item(name: str, session: ASesDep) -> ItemPublic:
    item_db = (await session.scalar(Item).where(Item.name == name))
    if item_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item_db

@router.patch("/")
async def partial_update_item(item: ItemUpdate, name: str, session: ASesDep) -> ItemPublic:
    item_db = (await session.scalar(Item).where(Item.name == name))
    if item_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    item_data = item.model_dump(exclude_unset=True, exclude_none=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    return item_db

@router.put("/")
async def update_item(item: ItemUpdate, name: str, session: ASesDep) -> ItemPublic:
    item_db = (await session.scalar(Item).where(Item.name == name))
    if item_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    item_data = item.model_dump()
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    return item_db


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(name: str, session: ASesDep):
    item_db = (await session.scalar(Item).where(Item.name == name))
    if item_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(item_db)

