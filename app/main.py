from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api
from app.core.config import settings
from app.db import create_db_and_tables
from app.db.models import load_all_models
from app.middleware import middleware
from app.utils import error_handler
from app.utils.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    await create_db_and_tables()
    load_all_models()
    yield


def get_app() -> FastAPI:
    """Create and return a FastAPI application instance."""

    app = FastAPI(
        lifespan=lifespan,
        debug=settings.DEBUG_MODE,
        openapi_url=f"/api/{settings.API_V1_STR}/openapi.json",
        docs_url=f"/api/{settings.API_V1_STR}/docs",
        redoc_url=None,
        middleware=middleware,
    )
    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Routers
    app.include_router(api.router)

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(
        RequestValidationError, error_handler.validation_exception_handler
    )
    app.add_exception_handler(Exception, error_handler.global_exception_handler)
    app.add_exception_handler(AppException, error_handler.app_exception_handler)
    return app


app = get_app()
