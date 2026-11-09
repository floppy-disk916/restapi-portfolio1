from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from .routes.item import router as item_router

app = FastAPI()
template = Jinja2Templates(directory="./src/templates")

from dataclasses import dataclass

@dataclass
class Item:
    name: str
    description: str

items: list[Item] = [
    Item(name="Jinja2",description="A library used for document templating"),
    Item(name="FastAPI", description="A backend framework well-known for its speed and simplicity"),
    Item(name="SQLAlchemy", description="A battle-tested ORM for python backend")
]


@app.get("/", include_in_schema=False)
async def main(request: Request):
    return template.TemplateResponse(
        request=request, name="index.html", context={"items": items}
    )

app.include_router(item_router)
