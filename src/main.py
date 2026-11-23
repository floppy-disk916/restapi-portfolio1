import logging
import traceback
from contextlib import asynccontextmanager

from drogue.adapters.fastapi import DrogueLimiter
from drogue.core.rules.rule import AlgorithmType, RateLimitRule

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .admin import router as admin_router
from .auth import router as auth_router
from .config import settings
from .db import (
    init_db,
    destroy_db,
)

from .libfix.drogue_extractors import FixedUserExtractor
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


def convert_repo_code(repo_code: int) -> int:
    match repo_code:
        case repository_code.REPOSITORY_GENERIC_ERR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case repository_code.REPOSITORY_INTERNAL_ERR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case repository_code.REPOSITORY_CONFLICT_ERR:
            return status.HTTP_409_CONFLICT
        case repository_code.REPOSITORY_MISSING_COL_ERR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case repository_code.REPOSITORY_NOT_FOUND_ERR:
            return status.HTTP_404_NOT_FOUND
        case repository_code.REPOSITORY_PARAM_ERR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR

def get_json_error_message(code: int) -> str:
    match code:
        case status.HTTP_500_INTERNAL_SERVER_ERROR:
            return "Internal server error. Try again later"
        case status.HTTP_409_CONFLICT:
            return "Data conflict"
        case status.HTTP_404_NOT_FOUND:
            return "Data not found"

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RepositoryException)
    async def repository_exc_handler(request: Request, exc: RepositoryException):
       
        logger.error(f"[Repository Error Message]: {exc.message}")
        
        code = convert_repo_code(exc.code)
        msg = get_json_error_message(code)

        return JSONResponse(
            status_code=code,
            content={
                "msg": f"{msg}",
            }
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
    yield

app = FastAPI(
    openapi_tags=tags,
    lifespan=lifespan,
    description=description,
    version=app_version,
    license_info=license_info,
    openapi_url=settings.openapi_url,
)

gcra_rule = RateLimitRule(
    limit=100,
    window=60,
    algorithm=AlgorithmType.GCRA,
    block=False,
    timeout=None,
    shadow=False,
)
GLOBAL_LIMITS = ["100/minute"]
GLOBAL_RULES = [gcra_rule]

limiter = DrogueLimiter(
    app=app,
    rules=GLOBAL_RULES,
    key_func=FixedUserExtractor(),
    default_limits=GLOBAL_LIMITS,
)

limited = limiter.limit

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

app.frontend("/", directory="dist", fallback="404.html")
app.include_router(admin_router)
app.include_router(main_router)
app.include_router(auth_router)

register_exception_handlers(app)
