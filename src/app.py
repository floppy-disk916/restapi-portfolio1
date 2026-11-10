from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from .routes.api import main_router

item_ops_available=5
staff_ops_available=0
app_title = "Warehouse Management"
app_description = "Web application for managing warehouse"

description = f"""
# {app_title}

## Item Operation

There are **{item_ops_available} path operations** available for item

## Staff Operation

There are **{staff_ops_available} path operations** available for staff
"""

tags = [
    {"name": "Item Operation", "description": "Operations for Item"},
    {"name": "Staff Operation", "description": "Operations for User"},
]

app = FastAPI(
    description=description,
    openapi_tags=tags,
    )
"""
template = Jinja2Templates(directory="./src/templates")

@app.get("/", include_in_schema=False)
async def main(request: Request):
    return template.TemplateResponse(
        request=request, name="index.html", context = {
            "app_title":app_title,
            "app_description":app_description
        },
    )
"""
app.include_router(main_router)
