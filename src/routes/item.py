from fastapi import APIRouter, status, HTTPException
from ..models import Item, ItemPublic
from ..db import ASesDep
from typing import Annotated

router = APIRouter(prefix="/item")


@router.post("/")
async def add_item(item: Item, session: ASesDep) -> ItemPublic:
    session.add(item)
    return item

@router.get("/")
async def get_item(name: str, session: ASesDep) -> ItemPublic:
    item = (await session.scalar(Item).where(Item.name == name))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item

@router.patch("/")
@router.delete("/")
@router.update("/")
