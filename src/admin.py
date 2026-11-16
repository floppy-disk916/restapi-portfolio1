from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin")

@router.post()
@router.get()
@router.put()
@router.patch()
@router.delete()
