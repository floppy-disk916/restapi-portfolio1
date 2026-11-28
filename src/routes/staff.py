from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from ..auth import check_api_key
from ..db import ASesDep
from ..models import Staff
from ..repository import get_async_repo
from ..schemas import StaffAdd, StaffPublic, StaffUpdate

router = APIRouter(tags=["Staff Operation"], prefix="/staff")

# Decide what type of model you want for the repository
Repo = get_async_repo(Staff, StaffPublic)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_staff(
    staff: StaffAdd, session: ASesDep, key: Annotated[str, Depends(check_api_key)]
) -> StaffPublic:
    return await Repo.create_one(session=session, data=staff)


@router.get("/")
async def get_staff(name: str, session: ASesDep) -> StaffPublic:
    return await Repo.get_one_by_id(session=session, _id=name, col="name")


@router.patch("/")
async def partial_update_staff(
    staff: StaffUpdate, name: str, session: ASesDep
) -> StaffPublic:
    return await Repo.patch_one_by_id(
        session=session, data=staff, _id=name, col="name"
    )


@router.put("/")
async def update_staff(staff: StaffUpdate, name: str, session: ASesDep) -> StaffPublic:
    try:
        staff_data = Staff.model_validate(staff.model_dump())
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return await Repo.update_one_by_id(
        session=session, data=staff_data, _id=name, col="name"
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(name: str, session: ASesDep):
    await Repo.remove_one_by_id(session=session, _id=name, col="name")
    return
