from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="./src/templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

@router.get("/doc")
async def doc(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="doc.html",
    )
