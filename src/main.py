
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi.errors import RateLimitExceeded

from .tracing import setup_tracing
from .admin import router as admin_router
from .auth import router as auth_router
from .config import settings
from .pages import router as page_router
from .db import (
    init_db,
    seed_test_staff,
    seed_test_item,
    seed_test_admin,
    delete_test_item,
    delete_test_staff,
    delete_test_admin,
    destroy_db,
    engine,
)

from .repository import (
    RepositoryException,
    repository_code,
)
from .routes.api import main_router


license_info = settings.license_info
app_version = settings.app_version
app_title = settings.app_title
app_description = settings.app_description
item_ops_available = 5
staff_ops_available = 5

description = f"""
# {app_title}
{app_description}

## Item Operation

There are **{item_ops_available} path operations** available for item

## Staff Operation

There are **{staff_ops_available} path operations** available for staff
"""

tags = [
    {"name": "Item Operation", "description": "Operations for Item"},
    {"name": "Staff Operation", "description": "Operations for User"},
]

logger = logging.getLogger(__name__)

def get_json_error_message(code: int) -> str:
    match code:
        case status.HTTP_500_INTERNAL_SERVER_ERROR:
            return "Internal server error. Try again later"
        case status.HTTP_409_CONFLICT:
            return "Data conflict"
        case status.HTTP_404_NOT_FOUND:
            return "Data not found"

def convert_repo_exc(exc: RepositoryException):

    kws = [
        "constraint",
    ]

    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    match exc.code:
        case repository_code.REPOSITORY_NOT_FOUND_ERR:
            code = status.HTTP_404_NOT_FOUND
        case repository_code.REPOSITORY_INTERNAL_ERR:
            code = status.HTTP_500_INTERNAL_SERVER_ERROR

    msg = "Internal error. Try again later"
    for kw in kws:
        if kw in exc.message:
            match kw:
                case "constraint":
                    code = status.HTTP_409_CONFLICT
                    msg = "Data conflict"

    data = {
        "status_code":code,
        "content":{
            "msg": msg,
        },
    }

    return data

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RepositoryException)
    async def repository_exc_handler(request: Request, exc: RepositoryException):
       
        logger.error(f"[Repository Error Message]: {exc.message}")
        
        data = convert_repo_exc(exc)
        return JSONResponse(
           **data, 
        )

    @app.exception_handler(Exception)
    async def internal_exc_handler(request: Request, exc: Exception):
        logger.error("\t\t========== Unhandled Error ==========\n\n")
        logger.error(
            "\n".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "msg": "Internal server error. Try again later",
            }
        ) 



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await init_db()
    await delete_test_admin()
    await delete_test_item()
    await delete_test_staff()
    if settings.mode in ["test", "dev"]:
        await seed_test_admin()
        await seed_test_item()
        await seed_test_staff()

    yield

    if settings.mode in ["test", "dev"]:
        await delete_test_admin()
        await delete_test_item()
        await delete_test_staff()
        await destroy_db()

app = FastAPI(
    openapi_tags=tags,
    lifespan=lifespan,
    description=description,
    version=app_version,
    license_info=license_info,
    openapi_url=settings.openapi_url,
)

GLOBAL_LIMITS = ["100/minute"]
REDIS_DSN = str(settings.redis_dsn)

limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=GLOBAL_LIMITS,
    storage_uri=REDIS_DSN,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIASGIMiddleware)



template = Jinja2Templates(directory="./src/templates")


@app.get("/", include_in_schema=False)
async def main(request: Request):
    return template.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_title": app_title, "app_description": app_description},
    )

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:443",
    "http://localhost:80",
]


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://localhost(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from pathlib import Path

path = Path(".")
dist_path = path / "dist"

if dist_path.exists():
    app.frontend("/", directory="dist", fallback="404.html")

app.include_router(admin_router)
app.include_router(main_router)
app.include_router(auth_router)
app.include_router(page_router)

setup_tracing(app, engine=engine)

if settings.tracing_enabled == True:
    register_exception_handlers(app)
