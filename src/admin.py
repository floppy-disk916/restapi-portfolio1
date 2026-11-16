from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", include_in_schema=False)
templates = Jinja2Templates(directory="./src/templates")

@router.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin.html"
    )
"""
@router.post()
@router.get()
@router.put()
@router.patch()
@router.delete()
"""
