import logging
import traceback
from contextlib import asynccontextmanager

from drogue.adapters.fastapi import DrogueLimiter
from .libfix.drogue_extractors import FixedUserExtractor

from drogue.core.rules.rule import AlgorithmType, RateLimitRule
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from .admin import router as admin_router
from .auth import router as auth_router
from .config import settings
from .db import (
    FactoryException,
    factory_code,
    init_db,
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


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(FactoryException)
    async def factory_exc_handler(request: Request, exc: FactoryException):
        logger.error(
            "Unhandled error: \n".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            ),
        )

        logger.error(f"\n\nMessage: {exc.message}\n\n")

        code: int = 0
        match exc.code:
            case (
                factory_code.FACTORY_ATTR_ERR
                | factory_code.FACTORY_MISSING_COL_ERR
                | factory_code.FACTORY_PARAM_ERR
            ):
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
                exc.message = "Internal server error"
            case factory_code.FACTORY_CONFLICT_ERR:
                code = status.HTTP_409_CONFLICT
                exc.message = "Data conflict"
            case factory_code.FACTORY_NOT_FOUND_ERR:
                code = status.HTTP_404_NOT_FOUND
                exc.message = "Data not found"
            case factory_code.FACTORY_GENERIC_ERR:
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
                exc.message = "Unknown error. Sorry"

        return JSONResponse(
            status_code=code,
            content={
                "code": exc.code,
                "error": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def internal_exc_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled error: \n".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            )
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "msg": "Something went wrong. Please try again later",
            },
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


app.frontend("/", directory="dist", fallback="404.html")
app.include_router(admin_router)
app.include_router(main_router)
app.include_router(auth_router)
register_exception_handlers(app)
