from fastapi import APIRouter

from .item import router as item_router
from .staff import router as staff_router

main_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")

v1_router.include_router(item_router)
v1_router.include_router(staff_router)
main_router.include_router(v1_router)
